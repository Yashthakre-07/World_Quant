import json
import requests
import time
import webbrowser
from pathlib import Path
from src.config import WQ_AUTH_URL, WQ_EMAIL, WQ_PASSWORD
from src.logger import agent_logger

class WQSession(requests.Session):
    def __init__(self):
        super().__init__()
        self.login_expired = False
        
        # Unique cookie file based on email to support switching profiles
        safe_email = WQ_EMAIL.replace("@", "_").replace(".", "_")
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
                    agent_logger.info(f"[AUTH] Reused existing authenticated session for {WQ_EMAIL}!")
                    is_authenticated = True
                else:
                    agent_logger.warning(f"[AUTH] Saved session cookies invalid or expired (status {r.status_code}).")
            except Exception as e:
                agent_logger.warning(f"[AUTH] Failed to verify saved session: {e}")
                
        if not is_authenticated:
            self.authenticate()

    def load_persisted_cookies(self):
        if self.cookies_path.exists():
            try:
                with open(self.cookies_path, "r") as f:
                    cookies = json.load(f)
                    self.cookies.update(cookies)
                agent_logger.info(f"[AUTH] Loaded cookies from {self.cookies_path.name}")
                return True
            except Exception as e:
                agent_logger.warning(f"[AUTH] Failed to load cookies: {e}")
        return False

    def save_persisted_cookies(self):
        self.cookies_path.parent.mkdir(exist_ok=True)
        try:
            cookies_dict = requests.utils.dict_from_cookiejar(self.cookies)
            with open(self.cookies_path, "w") as f:
                json.dump(cookies_dict, f, indent=2)
            agent_logger.info(f"[AUTH] Saved authenticated session cookies to {self.cookies_path.name}")
        except Exception as e:
            agent_logger.warning(f"[AUTH] Failed to save session cookies: {e}")

    def authenticate(self):
        if not WQ_EMAIL or not WQ_PASSWORD:
            agent_logger.error("[AUTH] Credentials not found in environment. Please set WQ_EMAIL and WQ_PASSWORD in your env file.")
            raise ValueError("Credentials missing.")

        self.auth = (WQ_EMAIL, WQ_PASSWORD)
        agent_logger.info(f"[AUTH] Attempting authentication with WorldQuant Brain for user: {WQ_EMAIL}")

        try:
            r = self.post(WQ_AUTH_URL)
            if r.status_code == 201 or 'user' in r.json():
                agent_logger.info("[AUTH] Successfully logged in to WorldQuant Brain!")
                self.login_expired = False
                self.save_persisted_cookies()
            elif 'inquiry' in r.json():
                inquiry = r.json()['inquiry']
                inquiry_id = inquiry.get('id') if isinstance(inquiry, dict) else inquiry
                biometric_url = f"{r.url}/persona?inquiry={inquiry_id}"
                import os
                is_headless = os.environ.get("RENDER") or not os.isatty(0)

                if is_headless:
                    # On Render: log the URL and poll automatically until verified
                    agent_logger.warning("=" * 60)
                    agent_logger.warning("[AUTH] BIOMETRIC VERIFICATION REQUIRED!")
                    agent_logger.warning(f"[AUTH] Open this URL in your browser to verify:")
                    agent_logger.warning(f"[AUTH] >>> {biometric_url} <<<")
                    agent_logger.warning("[AUTH] Polling for verification every 10 seconds...")
                    agent_logger.warning("=" * 60)
                    verified = False
                    for attempt in range(60):  # Wait up to 10 minutes
                        time.sleep(10)
                        p_r = self.post(f"https://api.worldquantbrain.com/authentication/persona", json=r.json())
                        if p_r.status_code == 201:
                            agent_logger.info("[AUTH] Biometric verification confirmed! Logged in successfully.")
                            self.login_expired = False
                            self.save_persisted_cookies()
                            verified = True
                            break
                        agent_logger.info(f"[AUTH] Waiting for browser verification... (attempt {attempt+1}/60)")
                    if not verified:
                        raise ValueError("Biometric verification timed out after 10 minutes.")
                else:
                    # Local machine: open browser and wait for Enter key
                    webbrowser.open(biometric_url)
                    input(f"Complete verification at: {biometric_url}\nThen press Enter here to continue...")
                    p_r = self.post(f"https://api.worldquantbrain.com/authentication/persona", json=r.json())
                    if p_r.status_code == 201:
                        agent_logger.info("[AUTH] Successfully logged in to WorldQuant Brain after Persona verification!")
                        self.login_expired = False
                        self.save_persisted_cookies()
                    else:
                        raise ValueError(f"Persona verification failed: {p_r.text}")
            else:
                resp_json = r.json()
                agent_logger.error(f"[AUTH] Authentication response warning: {resp_json}")
                raise ValueError(f"Login failed: {resp_json}")
        except Exception as e:
            agent_logger.error(f"[AUTH] Error during authentication: {e}")
            raise e
