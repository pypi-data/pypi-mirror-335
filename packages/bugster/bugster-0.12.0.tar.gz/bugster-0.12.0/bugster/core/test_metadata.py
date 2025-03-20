import os
import json
from bugster.config.paths import get_base_dir, get_credentials_path, get_traces_dir, get_screenshots_dir, ensure_dir_exists


class TestMetadata:
    """
    Reads and stores metadata about the current test run.
    For example:
    - Browser type (chromium, firefox, webkit)
    - Viewport size
    - Device emulation
    - Base URL
    - Credentials
    - Environment (dev, qa, prod)
    """

    def __init__(self, base_path: str = None, config_file: str = "bugster.json"):
        # Use the base_path from parameter or get it from paths module
        self.base_path = base_path if base_path is not None else get_base_dir()
        
        # Ensure the base directory exists
        ensure_dir_exists(self.base_path)
        
        # Use the credentials path from paths module
        self.config_file = get_credentials_path()
        self.config = {}
        self.current_env = "dev"  # Default environment
        
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)

    def get_browser(self, default: str = "chromium") -> str:
        return self.config.get("settings", {}).get("browser", default)

    def get_headless(self, default: bool = True) -> str:
        return self.config.get("settings", {}).get("headless", default)

    def get_viewport(self) -> dict:
        return self.config.get("settings", {}).get(
            "viewport", {"width": 1920, "height": 1080}
        )

    def get_credentials(self) -> dict:
        """
        Example: loads credentials from config or environment
        """
        creds = self.config.get("auth", {}).get("credentials", [])
        creds = {
            "email": creds[0].get("email", "test@example.com"),
            "password": creds[0].get("password", "secret"),
        }
        return creds

    def get_base_url(self) -> str:
        """Get the base URL for the current environment."""
        return (
            self.config.get("environment", {})
            .get(self.current_env, {})
            .get("base_url", "https://www.example.com")
        )

    def get_auth_url(self) -> str:
        return (
            self.config.get("environment", {})
            .get(self.current_env, {})
            .get("auth_url", "https://www.example.com")
        )

    def get_login_strategy(self):
        return self.config.get("auth", {}).get(
            "strategy", "default.path:BaseLoginStrategy"
        )

    def get_login_instructions(self):
        return self.config.get("auth", {}).get("instructions", {})

    def get_screenshot_path(self):
        """Get the path for screenshots using the paths module"""
        return get_screenshots_dir()

    def get_trace_path(self):
        """Get the path for traces using the paths module"""
        return get_traces_dir()