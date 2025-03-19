import requests
from ecotrade.utils import requires_auth

@requires_auth
def get_hermes_keys():
    try:
        api_url = "https://192.168.5.35:8080/get_hermes_credentials"
        response = requests.get(api_url, verify=False)
        
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"
        
        result = response.json()

        if "username" in result and "password" in result:
            username = result["username"]
            password = result["password"]
            return {"username": username, "password": password}
        else:
            return "Failed to retrieve Hermes credentials: Missing username or password in response"
    
    except requests.exceptions.RequestException as e:
        return f"Error during API call: {str(e)}"
