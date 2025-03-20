import json
import pkgutil
import requests
from QAnglesKit.auth import AuthManager

class qangleslqm:
    # Class-level variables to store configuration
    _config_loaded = False
    _lqm_url = None

    @classmethod
    def _load_config(cls):
        """Load API URLs from config.json once."""
        if not cls._config_loaded:
            config_data = pkgutil.get_data("QAnglesKit", "config.json")
            if config_data is None:
                raise FileNotFoundError("config.json not found in package.")
            
            config = json.loads(config_data.decode("utf-8"))
            cls._lqm_url = config["lqm_details_url"]

            # Ensure authentication is initialized
            if not AuthManager._login_url:
                AuthManager.initialize(config["login_url"])
            
            cls._config_loaded = True

    @classmethod
    def get_lqm_details(cls, domain):
        """
        Fetch LQM details for a given Domain. The Customer ID is retrieved automatically.
        
        Args:
            domain (str): Domain ID
        
        Returns:
            dict | None: JSON response containing LQM details or None if the request fails.
        """
        cls._load_config()  # Load configuration if not already loaded
        AuthManager.check_authentication()

        # Retrieve Customer ID from authentication credentials
        credentials = AuthManager.get_credentials()
        customer = credentials.get("customer_id")

        try:
            session = AuthManager.get_session()
            response = session.get(f"{cls._lqm_url}?DomainID={domain}&QAcustomerID={customer}")
            
            if response.status_code == 200:
                return response.json().get("Details")

            print(f"Failed to fetch LQM details: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching LQM details: {e}")
        return None


    # @classmethod
    # def get_lqm_all_execution_details(cls, domain, customer):
    #     """
    #     Fetch all LQM execution details for a given Domain and Customer using a POST request.
        
    #     Args:
    #         domain (str): Domain ID
    #         customer (str): Customer ID
        
    #     Returns:
    #         dict | None: JSON response containing all execution details or None if the request fails.
    #     """
    #     cls._load_config()
    #     AuthManager.check_authentication()

    #     try:
    #         session = AuthManager.get_session()
    #         response = session.post(cls._lqm_url, json={
    #             "Domain": domain,
    #             "Customer": customer,
    #             "Type": "AllExecutions"
    #         })
            
    #         if response.status_code == 200:
    #             return response.json().get("Details")
            
    #         print(f"Failed to fetch all LQM execution details: {response.status_code}")
    #     except requests.RequestException as e:
    #         print(f"Error fetching all LQM execution details: {e}")
    #     return None

    # @classmethod
    # def get_lqm_execution_details(cls, domain, customer, exe_id):
    #     """
    #     Fetch specific LQM execution details for a given Execution ID.
        
    #     Args:
    #         domain (str): Domain ID
    #         customer (str): Customer ID
    #         exe_id (str): Execution ID
        
    #     Returns:
    #         dict | None: JSON response containing execution details or None if the request fails.
    #     """
    #     cls._load_config()
    #     AuthManager.check_authentication()

    #     try:
    #         session = AuthManager.get_session()
    #         response = session.post(cls._lqm_url, json={
    #             "Domain": domain,
    #             "Customer": customer,
    #             "ExeID": exe_id
    #         })
            
    #         if response.status_code == 200:
    #             return response.json().get("Details")
            
    #         print(f"Failed to fetch LQM execution details: {response.status_code}")
    #     except requests.RequestException as e:
    #         print(f"Error fetching LQM execution details: {e}")
    #     return None



    # def get_lqm_all_execution_details(self, domain, customer):
    #     """Fetch all LQM execution details for a given Domain and Customer."""
    #     AuthManager.check_authentication()
    #     try:
    #         session = AuthManager.get_session()
    #         response = session.post(self.lqm_url, json={"Domain": domain, "Customer": customer, "Type": "AllExecutions"})
    #         if response.status_code == 200:
    #             return response.json().get("Details")
    #         print(f"Failed to fetch all LQM execution details: {response.status_code}")
    #     except requests.RequestException as e:
    #         print(f"Error fetching all LQM execution details: {e}")
    #     return None

    # def get_lqm_execution_details(self, domain, customer, exe_id):
    #     """Fetch specific LQM execution details for a given Execution ID."""
    #     AuthManager.check_authentication()
    #     try:
    #         session = AuthManager.get_session()
    #         response = session.post(self.lqm_url, json={"Domain": domain, "Customer": customer, "ExeID": exe_id})
    #         if response.status_code == 200:
    #             return response.json().get("Details")
    #         print(f"Failed to fetch LQM execution details: {response.status_code}")
    #     except requests.RequestException as e:
    #         print(f"Error fetching LQM execution details: {e}")
    #     return None
