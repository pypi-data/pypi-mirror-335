import requests
import getpass
import json
import pkgutil

class AuthManager:
    _session = requests.Session()
    _authenticated = False
    _email = None
    _password = None
    _customer_id = None
    _login_url = None

    @classmethod
    def initialize(cls, login_url):
        """Initialize login URL from config."""
        cls._login_url = login_url
        print(f"[DEBUG] Login URL initialized: {cls._login_url}")

    @classmethod
    def login(cls):
        """Handles user login and stores session details."""
        if cls._authenticated:
            print("Already logged in.")
            return True

        if cls._login_url is None:
            raise ValueError("Login URL not set. Call `initialize` first.")

        email = input("Enter your email: ")
        password = getpass.getpass("Enter your password: ")
        customer_id = email.split('@')[1].split('.')[0] if '@' in email else ""

        try:
            response = cls._session.post(cls._login_url, json={
                "Email": email,
                "password": password,
                "customerID": customer_id
            })
            if response.status_code == 200 and response.json().get("Status") == "Success":
                print("Login successful.")
                cls._authenticated = True
                cls._email = email
                cls._password = password
                cls._customer_id = customer_id
                return True
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"Error during login: {e}")
            return False

    @classmethod
    def logout(cls):
        """Clears authentication details."""
        cls._authenticated = False
        cls._email = None
        cls._password = None
        cls._customer_id = None
        print("Logged out successfully.")

    @classmethod
    def check_authentication(cls):
        """Raises an error if not logged in."""
        if not cls._authenticated:
            print("Not authenticated. Logging in now...")
            if not cls.login():
                raise Exception("Login failed. Cannot proceed.")

    @classmethod
    def get_session(cls):
        """Returns the active session object."""
        return cls._session

    @classmethod
    def get_credentials(cls):
        """Returns stored authentication details."""
        return {
            "email": cls._email,
            "customer_id": cls._customer_id,
            "authenticated": cls._authenticated,
            "userid":cls._email.split('@')[0] if '@' in cls._email else ""
        }
