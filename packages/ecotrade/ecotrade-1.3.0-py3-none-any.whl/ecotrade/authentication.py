import requests
import warnings
import urllib3

warnings.simplefilter('ignore', urllib3.exceptions.InsecureRequestWarning)

# Authentication 
class Auth:
    """
    Auth class for authenticating users by sending email and password to a remote API endpoint.
    
    Attributes:
        _authenticated (bool): Class variable that tracks whether the user is authenticated or not.
        email (str): User's email address for authentication.
        password (str): User's password for authentication.
        api_url (str): The URL of the authentication API endpoint.

    Methods:
        __init__(email: str, password: str):
            Initializes the Auth object with email and password.
            
        authenticate():
            Sends a POST request with the user's email and password to the API endpoint
            and checks if the authentication was successful.
            
    Example:
        auth = Auth(email="user@example.com", password="userpassword123")
        print(auth.authenticate())
    """
    
    _authenticated = False

    def __init__(self, email: str, password: str):
        """
        Initializes the Auth class with the user's email and password.
        
        Parameters:
            email (str): The user's email address.
            password (str): The user's password.
        """
        self.email = email
        self.password = password
        self.api_url = "https://192.168.5.35:8080/login" 

    def authenticate(self):
        """
        Sends a POST request to the API with the user's email and password and checks the response
        for authentication success or failure.

        Returns:
            str: A message indicating whether authentication was successful or not.
        """
        try:
            payload = {"email": self.email, "password": self.password}
            response = requests.post(self.api_url, json=payload, verify=False)
            
            if response.status_code != 200:
                return f"Error: Received status code {response.status_code}"
            
            result = response.json()

            if result.get("result") == "OK":
                Auth._authenticated = True
                return "Authentication successful"
            else:
                return "Failed to authenticate: Invalid credentials"

        except requests.exceptions.RequestException as e:
            return f"Error during authentication: {str(e)}"
