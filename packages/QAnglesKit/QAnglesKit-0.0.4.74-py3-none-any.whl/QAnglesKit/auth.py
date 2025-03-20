import requests
import json

class AuthManager:
    _session = requests.Session()
    _authenticated = False
    _token = None
    _customer_id = None
    _user_id = None
    _login_url = None

    @classmethod
    def initialize(cls, login_url):
        """Initialize login URL from config."""
        cls._login_url = login_url

    @classmethod
    def login(cls, token=None):
        """Handles user authentication using a token. If no token is provided, prompts for one."""
        if cls._authenticated:
            print("Already authenticated.")
            return True

        if cls._login_url is None:
            raise ValueError("Login URL not set. Call `initialize` first.")

        if token is None:
            token = input("Enter your authentication token: ")  # Prompt user for token

        try:
            response = cls._session.post(cls._login_url, json={"token": token})
            if response.status_code == 200:
                data = response.json()
                if data.get("Status") == "Success":
                    print("Authentication successful.")
                    cls._authenticated = True
                    cls._token = token
                    cls._customer_id = data.get("QAcustomerID")
                    cls._user_id = data.get("userID")
                    return True
                else:
                    print(f"Authentication failed: {data.get('Details')}")
                    return False
            else:
                print(f"Request failed: {response.status_code} - {response.text}")
                return False
        except requests.RequestException as e:
            print(f"Error during authentication: {e}")
            return False

    @classmethod
    def logout(cls):
        """Clears authentication details."""
        cls._authenticated = False
        cls._token = None
        cls._customer_id = None
        cls._user_id = None
        print("Logged out successfully.")

    @classmethod
    def check_authentication(cls):
        """Ensures the user is authenticated. If not, prompts for a token and logs in."""
        if not cls._authenticated:
            print("Not authenticated. Please enter your token to proceed.")
            if not cls.login():  # Calls login() which will prompt for token if not provided
                raise Exception("Authentication failed. Cannot proceed.")


    @classmethod
    def get_session(cls):
        """Returns the active session object."""
        return cls._session

    @classmethod
    def get_credentials(cls):
        """Returns stored authentication details."""
        return {
            "token": cls._token,
            "customer_id": cls._customer_id,
            "user_id": cls._user_id,
            "authenticated": cls._authenticated
        }
