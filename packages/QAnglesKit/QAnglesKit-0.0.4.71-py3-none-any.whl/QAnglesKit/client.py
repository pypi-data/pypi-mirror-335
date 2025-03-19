import json
import pkgutil
import requests
from QAnglesKit.auth import AuthManager

class QuantumJobDetails:
    def __init__(self):
        """Load API URLs from config.json and initialize authentication."""
        config_data = pkgutil.get_data("QAnglesKit", "config.json")
        if config_data is None:
            raise FileNotFoundError("config.json not found in package.")

        config = json.loads(config_data.decode("utf-8"))
        self.fetch_url = config["fetch_jobdetails_url"]
        self.store_url = config["store_jobdetails_url"]
        self.get_all_url = config["get_all_jobdetails_url"]

        # ✅ Ensure authentication is initialized
        if not AuthManager._login_url:
            AuthManager.initialize(config["login_url"])

    def fetch_job_details(self, job_id):
        """Fetch details of a quantum job by its ID."""
        AuthManager.check_authentication()
        try:
            session = AuthManager.get_session()
            response = session.post(self.fetch_url, json={"job_id": job_id})
            return response.json().get("Details") if response.status_code == 200 else None
        except requests.RequestException as e:
            print(f"Error while fetching job details: {e}")
            return None

    def store_job_details(self, job_data):
        """Store new quantum job details."""
        AuthManager.check_authentication()
        try:
            session = AuthManager.get_session()
            response = session.post(self.store_url, json=job_data)
            return response.json().get("Details") if response.status_code in [200, 201] else None
        except requests.RequestException as e:
            print(f"Error while saving job: {e}")
            return None

    def get_all_jobs(self):
        """Retrieve all stored quantum jobs."""
        AuthManager.check_authentication()
        try:
            session = AuthManager.get_session()
            response = session.get(self.get_all_url)
            return response.json().get("Details") if response.status_code == 200 else None
        except requests.RequestException as e:
            print(f"Error while fetching all jobs: {e}")
            return None
