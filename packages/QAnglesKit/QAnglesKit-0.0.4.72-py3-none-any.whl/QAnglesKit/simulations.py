import json
import pkgutil
import requests
import uuid
from QAnglesKit.auth import AuthManager

class qanglessimulation:
    _config_loaded = False
    _simulation_url = None
    _simulation_create_url = None

    @classmethod
    def _load_config(cls):
        """Load API URLs from config.json once."""
        if not cls._config_loaded:
            config_data = pkgutil.get_data("QAnglesKit", "config.json")
            if config_data is None:
                raise FileNotFoundError("config.json not found in package.")
            
            config = json.loads(config_data.decode("utf-8"))
            cls._simulation_url = config["simulation_custom_url"]
            cls._simulation_create_url = config["simulation_create_url"]

            if not AuthManager._login_url:
                AuthManager.initialize(config["login_url"])
            
            cls._config_loaded = True

    @classmethod
    def get_simulation_details(cls, ProjectID, DomainID):
        """Fetch simulation details using stored credentials."""
        cls._load_config()
        AuthManager.check_authentication()

        credentials = AuthManager.get_credentials()
        QAcustomerID = credentials.get("customer_id")

        try:
            session = AuthManager.get_session()
            response = session.post(cls._simulation_url, json={
                "QAcustomerID": QAcustomerID,
                "ProjectID": ProjectID,
                "DomainID": DomainID,
                "start": 0,
                "end": 10
            })
            if response.status_code == 200:
                return response.json()
            print(f"Failed to fetch simulation details: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching simulation details: {e}")
        return None
    
    @classmethod
    def create_simulation(cls, DomainID, simulationName, ProjectID, simulationDescription):
        """Create a new simulation using stored credentials."""
        cls._load_config()
        AuthManager.check_authentication()

        credentials = AuthManager.get_credentials()
        QAcustomerID = credentials.get("customer_id")
        userID = credentials.get("userid")
        userName = userID  # Assuming username is same as userID

        try:
            session = AuthManager.get_session()
            sessionID = str(uuid.uuid4())
            response = session.post(cls._simulation_create_url, json={
                "QAcustomerID": QAcustomerID,
                "DomainID": DomainID,
                "userID": userID,
                "sessionID": sessionID,
                "simulationName": simulationName,
                "simulationDesc": simulationDescription,
                "userName": userName,
                "ProjectID": ProjectID,
                "simulationUrl": "simulationUrl"
            })
            if response.status_code == 200:
                return response.json()
            print(f"Failed to create simulation: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error creating simulation: {e}")
        return None
