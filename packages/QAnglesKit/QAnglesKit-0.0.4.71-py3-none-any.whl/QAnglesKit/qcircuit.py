import json
import pkgutil
import requests
from QAnglesKit.auth import AuthManager

class qanglesqcircuit:
    # Class-level variables to store configuration
    _config_loaded = False
    _qcircuit_url = None

    @classmethod
    def _load_config(cls):
        """Load API URLs from config.json once."""
        if not cls._config_loaded:
            config_data = pkgutil.get_data("QAnglesKit", "config.json")
            if config_data is None:
                raise FileNotFoundError("config.json not found in package.")

            config = json.loads(config_data.decode("utf-8"))
            cls._qcircuit_url = config["qcircuit_url"]

            # Ensure authentication is initialized
            if not AuthManager._login_url:
                AuthManager.initialize(config["login_url"])

            cls._config_loaded = True

    @classmethod
    def get_qcircuit_details(cls, domain):
        """
        Fetch quantum circuit details for a given Domain. The Customer ID is retrieved automatically.
        
        Args:
            domain (str): Domain ID
        
        Returns:
            dict | None: JSON response containing quantum circuit details or None if the request fails.
        """
        cls._load_config()  # Load configuration if not already loaded
        AuthManager.check_authentication()

        # Retrieve Customer ID from authentication credentials
        credentials = AuthManager.get_credentials()
        customer = credentials.get("customer_id")

        try:
            session = AuthManager.get_session()
            response = session.post(cls._qcircuit_url, json={"Domain": domain, "Customer": customer})
            
            if response.status_code == 200:
                return response.json().get("Details")

            print(f"Failed to fetch quantum circuit details: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching quantum circuit details: {e}")
        return None
