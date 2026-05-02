import os
import instaloader
from utils.logger import logger

class InstagramAuthManager:
    def __init__(self, L: instaloader.Instaloader, session_file: str = "ig_session"):
        self.L = L
        self.session_file = session_file

    def login(self, username: str = None, password: str = None):
        """Attempt to load session, or login via credentials."""
        try:
            if os.path.exists(self.session_file):
                logger.info(f"Loading Instagram session from {self.session_file}...")
                self.L.load_session_from_file(username, filename=self.session_file)
                logger.info("Session loaded successfully.")
                return True
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")

        if username and password:
            logger.info(f"Attempting login for {username}...")
            try:
                self.L.login(username, password)
                self.L.save_session_to_file(self.session_file)
                logger.info("Login successful. Session saved.")
                return True
            except instaloader.exceptions.BadCredentialsException:
                logger.error("Invalid Instagram credentials.")
            except instaloader.exceptions.TwoFactorAuthRequiredException:
                logger.error("2FA required. Please login manually and provide the session file.")
            except Exception as e:
                logger.error(f"Login failed: {e}")
        
        logger.info("Proceeding as anonymous user (some content may be restricted).")
        return False
