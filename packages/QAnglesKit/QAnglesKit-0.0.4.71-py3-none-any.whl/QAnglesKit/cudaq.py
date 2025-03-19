import json
import pkgutil
import requests
import base64
from io import BytesIO
from PIL import Image
import IPython.display as display
from QAnglesKit.auth import AuthManager

class qanglescuda:
    _config_loaded = False
    _cudaq_url = None
    _cudaq_algo_url = None
    _cudaq_algo_exec_url = None

    @classmethod
    def _load_config(cls):
        """Load API URLs from config.json once."""
        if not cls._config_loaded:
            config_data = pkgutil.get_data("QAnglesKit", "config.json")
            if config_data is None:
                raise FileNotFoundError("config.json not found in package.")
            
            config = json.loads(config_data.decode("utf-8"))
            cls._cudaq_url = config["cudaq_url"]
            cls._cudaq_algo_url = config["cudaq_algo_url"]
            cls._cudaq_algo_exec_url = config["cudaq_algo_exec_url"]

            if not AuthManager._login_url:
                AuthManager.initialize(config["login_url"])
            
            cls._config_loaded = True

    @classmethod
    def get_cudaq_details(cls):
        """Fetch and format CUDA-Q algorithm details."""
        cls._load_config()
        AuthManager.check_authentication()
        try:
            session = AuthManager.get_session()
            response = session.get(cls._cudaq_url)
            if response.status_code == 200:
                data = response.json()
                return [{"AlgoName": algo["AlgoName"], "AlgoID": algo["AlgoID"]} for algo in data]
            print(f"Failed to fetch CUDA-Q details: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching CUDA-Q details: {e}")
        return None

    @classmethod
    def get_cudaq_algo_details(cls, AlgoId):
        """Fetch CUDA-Q algorithm details using AlgoID in the URL."""
        cls._load_config()
        AuthManager.check_authentication()
        try:
            session = AuthManager.get_session()
            url = f"{cls._cudaq_algo_url}?AlgoID={AlgoId}"
            response = session.get(url)
            if response.status_code == 200:
                return response.json()
            print(f"Failed to fetch CUDA-Q algorithm details: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching CUDA-Q algorithm details: {e}")
        return None

    @classmethod
    def get_cudaq_algo_execution_details(cls, algo_name, hardware_run_id, algo_run_id):
        """Fetch CUDA-Q algorithm execution details and display the circuit diagram if available."""
        cls._load_config()
        AuthManager.check_authentication()

        credentials = AuthManager.get_credentials()
        qa_customer_id = credentials.get("customer_id")

        try:
            session = AuthManager.get_session()
            params = {
                "AlgoName": algo_name,
                "HardwareRunID": hardware_run_id,
                "QAcustomerID": qa_customer_id,
                "AlgoRunID": algo_run_id
            }
            response = session.get(cls._cudaq_algo_exec_url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                # Extract HardwareCircuitDiagram from HardwareRunResults
                hardware_results = data.get("HardwareRunResults", [])
                if len(hardware_results) > 4 and isinstance(hardware_results[4], dict):
                    image_data_base64 = hardware_results[4].get("HardwareCircuitDiagram")
                    if image_data_base64:
                        try:

                            image_data = base64.b64decode(image_data_base64)
                            image = Image.open(BytesIO(image_data))
                            
                            # Display image in Jupyter Notebook
                            display.display(image)
                        except Exception as e:
                            print(f"Error displaying image: {e}")
                
                return None
            print(f"Failed to fetch CUDA-Q execution details: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching CUDA-Q execution details: {e}")
        return None