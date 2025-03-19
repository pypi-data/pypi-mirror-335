import json
import pkgutil
import requests
import uuid
from QAnglesKit.auth import AuthManager

class qanglesproject:
    _config_loaded = False
    _project_url = None
    _project_create_url = None

    @classmethod
    def _load_config(cls):
        """Load API URLs from config.json once."""
        if not cls._config_loaded:
            config_data = pkgutil.get_data("QAnglesKit", "config.json")
            if config_data is None:
                raise FileNotFoundError("config.json not found in package.")
            
            config = json.loads(config_data.decode("utf-8"))
            cls._project_url = config["project_system_url"]
            cls._project_create_url = config["project_create_url"]
            
            if not AuthManager._login_url:
                AuthManager.initialize(config["login_url"])
            
            cls._config_loaded = True

    @classmethod
    def get_project_details(cls, DomainID, projectType):
        """Fetch project details using stored credentials."""
        cls._load_config()
        AuthManager.check_authentication()

        credentials = AuthManager.get_credentials()
        QAcustomerID = credentials.get("customer_id")
        userID = credentials.get("userid")

        try:
            session = AuthManager.get_session()
            response = session.post(cls._project_url, json={
                "QAcustomerID": QAcustomerID,
                "DomainID": DomainID,
                "start": 0,
                "end": 10,
                "userID": userID,
                "projectType": projectType
            })
            if response.status_code == 200:
                return response.json()
            print(f"Failed to fetch project details: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching project details: {e}")
        return None
    
    @classmethod
    def create_project(cls, DomainID, ProjectName, ProjectDescription):
        """Create a new project using stored credentials."""
        cls._load_config()
        AuthManager.check_authentication()

        credentials = AuthManager.get_credentials()
        QAcustomerID = credentials.get("customer_id")
        userID = credentials.get("userid")
        userName = userID  # Assuming username is same as userID

        try:
            session = AuthManager.get_session()
            sessionID = str(uuid.uuid4())
            response = session.post(cls._project_create_url, json={
                "QAcustomerID": QAcustomerID,
                "DomainID": DomainID,
                "userID": userID,
                "sessionID": sessionID,
                "ProjectName": ProjectName,
                "ProjectDescription": ProjectDescription,
                "userName": userName,
                "userAccess": []
            })
            if response.status_code == 200:
                return response.json()
            print(f"Failed to create project: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error creating project: {e}")
        return None
