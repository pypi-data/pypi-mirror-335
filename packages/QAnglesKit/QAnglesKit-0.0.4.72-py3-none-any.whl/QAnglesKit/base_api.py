import requests
import json
import pkgutil
from QAnglesKit.auth import AuthManager

class BaseAPIHandler:
    def __init__(self):
        """Initialize with API URLs from config.json."""
        self.session = AuthManager.get_session()
        self.authenticated = AuthManager._authenticated
        self.urls = self.load_config()

    def load_config(self):
        """Load API URLs from config.json."""
        config_data = pkgutil.get_data("QAnglesKit", "config.json")
        if config_data is None:
            raise FileNotFoundError("Config file not found.")
        return json.loads(config_data.decode("utf-8"))

    def check_authentication(self):
        """Ensure user is authenticated before making requests."""
        if not self.authenticated:
            print("Not authenticated. Logging in now...")
            if not AuthManager.login():
                raise Exception("Login failed. Cannot proceed.")

    def make_request(self, url_key, payload):
        """Make a POST request to the given API."""
        self.check_authentication()
        url = self.urls.get(url_key)
        if not url:
            raise ValueError(f"URL for {url_key} not found in config.json")
        
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                return response.json().get("Details")
            print(f"API Request Failed: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error in API request: {e}")
        return None
