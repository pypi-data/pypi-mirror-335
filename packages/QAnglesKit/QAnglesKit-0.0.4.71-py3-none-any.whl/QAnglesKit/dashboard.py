import json
import pkgutil
import requests
from QAnglesKit.auth import AuthManager

class qanglesdashboard:
    # Class-level variables to store configuration
    _config_loaded = False
    _dashboard_url = None

    @classmethod
    def _load_config(cls):
        """Load API URLs from config.json once."""
        if not cls._config_loaded:
            config_data = pkgutil.get_data("QAnglesKit", "config.json")
            if config_data is None:
                raise FileNotFoundError("config.json not found in package.")

            config = json.loads(config_data.decode("utf-8"))
            cls._dashboard_url = config["dashboard_url"]

            # Ensure authentication is initialized
            if not AuthManager._login_url:
                AuthManager.initialize(config["login_url"])

            cls._config_loaded = True

    @classmethod
    def get_dashboard(cls, domain_id):
        """
        Fetch dashboard data based on DomainID. Customer and UserID are retrieved automatically.
        
        Args:
            domain_id (str): The domain ID
        
        Returns:
            dict | None: JSON response containing dashboard data or None if the request fails.
        """
        cls._load_config()  # Load configuration if not already loaded
        AuthManager.check_authentication()

        # Retrieve Customer ID and User ID from authentication credentials
        credentials = AuthManager.get_credentials()
        customer = credentials.get("customer_id")
        user_id = credentials.get("user_id")

        try:
            session = AuthManager.get_session()
            response = session.post(cls._dashboard_url, json={
                "QAcustomerID": customer,
                "DomainID": domain_id,
                "userID": user_id,
                "Key": 1
            })

            if response.status_code == 200:
                return response.json().get("boxesdata2")

            print(f"Failed to fetch dashboard data: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching dashboard data: {e}")
        return None
