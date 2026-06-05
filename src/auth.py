# ==============================================================================
# CRITICAL CONSTRAINTS WARNING:
# - NO GITHUB PUSH: NEVER TRIGGER GIT PUSH FROM THE AGENT CONTEXT OR SCRIPTS.
# - NO BIOMETRIC TRIGGER: NEVER TRIGGER PERSONA BIOMETRIC VERIFICATION FLOWS.
# ==============================================================================

import json
import requests
import time
import webbrowser
from pathlib import Path
from src.config import WQ_AUTH_URL
import src.config
from src.logger import agent_logger
import logging
import urllib3
import os

os.environ.pop("REQUESTS_CA_BUNDLE", None)
os.environ.pop("SSL_CERT_FILE", None)
os.environ.pop("CURL_CA_BUNDLE", None)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log_callback = None

def set_log_callback(cb):
    global log_callback
    log_callback = cb

def log_auth(level, msg):
    # Log to native python agent logger
    lvl = logging.ERROR if level == "ERROR" else (logging.WARNING if level == "WARNING" else logging.INFO)
    agent_logger.log(lvl, msg)
    
    # Push to pipeline state log stream if registered
    if log_callback:
        try:
            log_callback(level, msg)
        except Exception:
            pass

class PersonaRequiredException(Exception):
    def __init__(self, url, inquiry_payload, session=None):
        self.url = url
        self.inquiry_payload = inquiry_payload
        self.session = session
        super().__init__(f"Persona biometric verification required: {url}")

class WQSession(requests.Session):
    def __init__(self, email=None, password=None, interactive=False, cli_mode=False, allow_biometrics=False):
        super().__init__()
        self.verify = False
        self.login_expired = False
        self.interactive = interactive
        self.cli_mode = cli_mode
        self.allow_biometrics = allow_biometrics
        self.email = email if email else src.config.WQ_EMAIL
        self.password = password if password else src.config.WQ_PASSWORD
        
        # Unique cookie file based on email to support switching profiles
        safe_email = self.email.replace("@", "_").replace(".", "_")
        self.cookies_path = src.config.DB_DIR / f"session_cookies_{safe_email}.json"
        
        # Try loading persisted cookies
        cookies_loaded = self.load_persisted_cookies()
        
        # Verify if cookies are still valid
        is_authenticated = False
        if cookies_loaded:
            try:
                # GET /users/self is protected and returns 200 if logged in
                r = self.get("https://api.worldquantbrain.com/users/self", timeout=15)
                if r.status_code == 200:
                    log_auth("INFO", f"[AUTH] Reused existing authenticated session for {self.email}!")
                    is_authenticated = True
                else:
                    log_auth("WARNING", f"[AUTH] Saved session cookies invalid or expired (status {r.status_code}).")
            except Exception as e:
                log_auth("WARNING", f"[AUTH] Failed to verify saved session: {e}")
                
        if not is_authenticated:
            # ONLY attempt automatic login/authentication if interactive or in cli_mode!
            # During background deploy/startup, we defer login entirely until the user interactively triggers it.
            if self.interactive or self.cli_mode:
                self.authenticate(allow_biometrics=allow_biometrics)
            else:
                self.login_expired = True
                log_auth("INFO", f"[AUTH] Background startup/deploy detected. Skipping authentication attempt silently for {self.email}. Session will be activated when you click 'Re-auth Session' on the dashboard.")

    def load_persisted_cookies(self):
        if self.cookies_path.exists():
            try:
                with open(self.cookies_path, "r") as f:
                    cookies = json.load(f)
                    self.cookies.update(cookies)
                log_auth("INFO", f"[AUTH] Loaded cookies from {self.cookies_path.name}")
                return True
            except Exception as e:
                log_auth("WARNING", f"[AUTH] Failed to load cookies: {e}")
        return False

    def save_persisted_cookies(self):
        self.cookies_path.parent.mkdir(exist_ok=True)
        try:
            cookies_dict = requests.utils.dict_from_cookiejar(self.cookies)
            with open(self.cookies_path, "w") as f:
                json.dump(cookies_dict, f, indent=2)
            log_auth("INFO", f"[AUTH] Saved authenticated session cookies to {self.cookies_path.name}")
        except Exception as e:
            log_auth("WARNING", f"[AUTH] Failed to save session cookies: {e}")

    def authenticate(self, allow_biometrics=False):
        if not self.email or not self.password:
            log_auth("ERROR", f"[AUTH] Credentials not found. Please verify they are correctly configured.")
            raise ValueError("Credentials missing.")

        self.auth = (self.email, self.password)
        log_auth("INFO", f"[AUTH] Attempting authentication with WorldQuant Brain for user: {self.email}")

        try:
            r = self.post(WQ_AUTH_URL)
            if r.status_code == 201 or 'user' in r.json():
                log_auth("INFO", "[AUTH] Successfully logged in to WorldQuant Brain!")
                self.login_expired = False
                self.save_persisted_cookies()
            elif 'inquiry' in r.json():
                if not allow_biometrics:
                    log_auth("WARNING", "[AUTH] Biometric verification was required by WorldQuant Brain, but biometric triggers are disabled by default/operator command.")
                    raise ValueError("Biometric verification disabled by default")
                
                resp_json = r.json()
                inquiry = resp_json.get('inquiry', {})

                # inquiry can be a plain string ID or a dict {id: ..., url: ...}
                if isinstance(inquiry, str):
                    inquiry_id = inquiry
                    inquiry_url_from_resp = None
                elif isinstance(inquiry, dict):
                    inquiry_id = inquiry.get('id') or inquiry.get('inquiry_id') or ''
                    inquiry_url_from_resp = inquiry.get('url') or inquiry.get('redirect_url') or ''
                else:
                    inquiry_id = ''
                    inquiry_url_from_resp = None

                # Build biometric URL — try sources in best→worst order
                biometric_url = None

                # 1. Direct Persona verification link (most reliable, bypasses WQ wrapper)
                if inquiry_id:
                    biometric_url = f"https://inquiry.withpersona.com/verify?inquiry-id={inquiry_id}"

                # 2. URL field from the response JSON
                if not biometric_url and inquiry_url_from_resp:
                    biometric_url = inquiry_url_from_resp

                # 3. Location header fallback
                if not biometric_url and 'Location' in r.headers:
                    from urllib.parse import urljoin
                    biometric_url = urljoin(r.url, r.headers['Location'])
                    if "api.worldquantbrain.com" in biometric_url:
                        biometric_url = biometric_url.replace(
                            "api.worldquantbrain.com", "platform.worldquantbrain.com"
                        )

                # 4. Hard fallback to platform login page (user can manually log in)
                if not biometric_url:
                    biometric_url = "https://platform.worldquantbrain.com/sign-in"
                    log_auth("WARNING", "[AUTH] Could not extract Persona URL from WQ response. Falling back to platform login page.")

                log_auth("INFO", f"[AUTH] Biometric verification URL resolved: {biometric_url}")

                if self.interactive:
                    raise PersonaRequiredException(biometric_url, resp_json, self)
                elif self.cli_mode:
                    # Direct CLI execution (e.g., manual script execution on terminal): display link and wait
                    import os
                    is_headless = os.environ.get("RENDER") or not os.isatty(0)

                    if is_headless:
                        # On Render CLI: log the URL and poll automatically until verified
                        log_auth("WARNING", "=" * 60)
                        log_auth("WARNING", "[AUTH] BIOMETRIC VERIFICATION REQUIRED!")
                        log_auth("WARNING", f"[AUTH] Open this URL in your browser to verify:")
                        log_auth("WARNING", f"[AUTH] >>> {biometric_url} <<<")
                        log_auth("WARNING", "[AUTH] Polling for verification every 10 seconds...")
                        log_auth("WARNING", "=" * 60)
                        verified = False
                        for attempt in range(60):  # Wait up to 10 minutes
                            time.sleep(10)
                            p_r = self.post(f"https://api.worldquantbrain.com/authentication/persona", json=resp_json)
                            if p_r.status_code == 201:
                                log_auth("INFO", "[AUTH] Biometric verification confirmed! Logged in successfully.")
                                self.login_expired = False
                                self.save_persisted_cookies()
                                verified = True
                                break
                            log_auth("INFO", f"[AUTH] Waiting for browser verification... (attempt {attempt+1}/60)")
                        if not verified:
                            raise ValueError("Biometric verification timed out after 10 minutes.")
                    else:
                        # Local machine CLI: open browser and wait for Enter key
                        webbrowser.open(biometric_url)
                        input(f"Complete verification at: {biometric_url}\nThen press Enter here to continue...")
                        p_r = self.post(f"https://api.worldquantbrain.com/authentication/persona", json=resp_json)
                        if p_r.status_code == 201:
                            log_auth("INFO", "[AUTH] Successfully logged in to WorldQuant Brain after Persona verification!")
                            self.login_expired = False
                            self.save_persisted_cookies()
                        else:
                            raise ValueError(f"Persona verification failed: {p_r.text}")
                else:
                    # Headless Background Startup / Deploy: Raise exception to halt loops and prevent account blockage
                    self.login_expired = True
                    log_auth("WARNING", f"[AUTH] Biometric verification is required for {self.email}. Halting execution to prevent automated account blockages.")
                    raise PersonaRequiredException(biometric_url, resp_json, self)
            else:
                err_json = r.json()
                detail = err_json.get("detail", "")
                if "BIOMETRICS_THROTTLED" in str(detail):
                    log_auth("WARNING", "[AUTH] WorldQuant Brain has throttled biometric requests. Please wait 5-10 minutes before requesting a new login.")
                    raise ValueError("BIOMETRICS_THROTTLED: Please wait 5-10 minutes for the platform cooldown to expire before attempting re-authentication.")
                
                log_auth("ERROR", f"[AUTH] Authentication response warning: {err_json}")
                raise ValueError(f"Login failed: {err_json}")
        except Exception as e:
            log_auth("ERROR", f"[AUTH] Error during authentication: {e}")
            raise e

