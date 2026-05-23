import json
import requests
import time
import webbrowser
from pathlib import Path
from src.config import WQ_AUTH_URL
import src.config
from src.logger import agent_logger
import logging

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
    def __init__(self, url, inquiry_payload):
        self.url = url
        self.inquiry_payload = inquiry_payload
        super().__init__(f"Persona biometric verification required: {url}")

class WQSession(requests.Session):
    def __init__(self, interactive=False):
        super().__init__()
        self.login_expired = False
        self.interactive = interactive
        
        # Unique cookie file based on email to support switching profiles
        safe_email = src.config.WQ_EMAIL.replace("@", "_").replace(".", "_")
        self.cookies_path = Path(__file__).resolve().parent.parent / "db" / f"session_cookies_{safe_email}.json"
        
        # Try loading persisted cookies
        cookies_loaded = self.load_persisted_cookies()
        
        # Verify if cookies are still valid
        is_authenticated = False
        if cookies_loaded:
            try:
                # GET /users/self is protected and returns 200 if logged in
                r = self.get("https://api.worldquantbrain.com/users/self", timeout=15)
                if r.status_code == 200:
                    log_auth("INFO", f"[AUTH] Reused existing authenticated session for {src.config.WQ_EMAIL}!")
                    is_authenticated = True
                else:
                    log_auth("WARNING", f"[AUTH] Saved session cookies invalid or expired (status {r.status_code}).")
            except Exception as e:
                log_auth("WARNING", f"[AUTH] Failed to verify saved session: {e}")
                
        if not is_authenticated:
            self.authenticate()

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

    def authenticate(self):
        if not src.config.WQ_EMAIL or not src.config.WQ_PASSWORD:
            log_auth("ERROR", "[AUTH] Credentials not found in environment. Please set WQ_EMAIL and WQ_PASSWORD in your env file.")
            raise ValueError("Credentials missing.")

        self.auth = (src.config.WQ_EMAIL, src.config.WQ_PASSWORD)
        log_auth("INFO", f"[AUTH] Attempting authentication with WorldQuant Brain for user: {src.config.WQ_EMAIL}")

        try:
            r = self.post(WQ_AUTH_URL)
            if r.status_code == 201 or 'user' in r.json():
                log_auth("INFO", "[AUTH] Successfully logged in to WorldQuant Brain!")
                self.login_expired = False
                self.save_persisted_cookies()
            elif 'inquiry' in r.json():
                inquiry = r.json()['inquiry']
                inquiry_id = inquiry.get('id') if isinstance(inquiry, dict) else inquiry
                biometric_url = f"{r.url}/persona?inquiry={inquiry_id}"
                
                if self.interactive:
                    raise PersonaRequiredException(biometric_url, r.json())
                
                import os
                is_headless = os.environ.get("RENDER") or not os.isatty(0)

                if is_headless:
                    # On Render: log the URL and poll automatically until verified
                    log_auth("WARNING", "=" * 60)
                    log_auth("WARNING", "[AUTH] BIOMETRIC VERIFICATION REQUIRED!")
                    log_auth("WARNING", f"[AUTH] Open this URL in your browser to verify:")
                    log_auth("WARNING", f"[AUTH] >>> {biometric_url} <<<")
                    log_auth("WARNING", "[AUTH] Polling for verification every 10 seconds...")
                    log_auth("WARNING", "=" * 60)
                    verified = False
                    for attempt in range(60):  # Wait up to 10 minutes
                        time.sleep(10)
                        p_r = self.post(f"https://api.worldquantbrain.com/authentication/persona", json=r.json())
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
                    # Local machine: open browser and wait for Enter key
                    webbrowser.open(biometric_url)
                    input(f"Complete verification at: {biometric_url}\nThen press Enter here to continue...")
                    p_r = self.post(f"https://api.worldquantbrain.com/authentication/persona", json=r.json())
                    if p_r.status_code == 201:
                        log_auth("INFO", "[AUTH] Successfully logged in to WorldQuant Brain after Persona verification!")
                        self.login_expired = False
                        self.save_persisted_cookies()
                    else:
                        raise ValueError(f"Persona verification failed: {p_r.text}")
            else:
                resp_json = r.json()
                log_auth("ERROR", f"[AUTH] Authentication response warning: {resp_json}")
                raise ValueError(f"Login failed: {resp_json}")
        except Exception as e:
            log_auth("ERROR", f"[AUTH] Error during authentication: {e}")
            raise e
