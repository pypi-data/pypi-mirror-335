import requests
import warnings
import urllib3

warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)
class Auth:
    _authenticated = False

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.api_url = "https://192.168.5.35:8080/login" 

    def authenticate(self):
        try:
            payload = {"email": self.email, "password": self.password}
            response = requests.post(self.api_url, json=payload, verify=False)
            if response.status_code != 200:
                return f"Error: Received status code {response.status_code}"
            result = response.json()

            if result.get("result") == "OK":
                Auth._authenticated = True
                return f"Authentication successful"
            else:
                return "Failed to authenticate: Invalid credentials"

        except requests.exceptions.RequestException as e:
            return f"Error during authentication: {str(e)}"
