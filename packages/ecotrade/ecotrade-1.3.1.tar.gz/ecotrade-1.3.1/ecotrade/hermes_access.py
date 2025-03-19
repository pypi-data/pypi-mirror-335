import requests
from ecotrade.utils import requires_auth

@requires_auth
def get_hermes_keys():
    """
    This function retrieves the Hermes credentials by making a GET request to a specified API endpoint. 
    The endpoint is expected to return a JSON object containing the 'username' and 'password' required for 
    accessing the Hermes system.

    Steps:
    1. Sends a GET request to the 'https://192.168.5.35:8080/get_hermes_credentials' API endpoint.
    2. If the request is successful (status code 200), it checks if the response contains both a 'username' and a 'password'.
    3. If the required fields are found, the function returns a dictionary containing the 'username' and 'password'.
    4. If any of the required fields are missing, an error message is returned indicating missing credentials.
    5. If the API request fails (for example, if there is a connection issue), an error message is returned indicating the problem.
    
    Parameters:
    - None directly, but the function uses an authenticated session (via the `@requires_auth` decorator) to ensure the request is made by an authorized user.

    Returns:
    - If successful, a dictionary containing the 'username' and 'password' for Hermes credentials.
    - If unsuccessful (e.g., if the credentials are missing from the response or an error occurs during the API call), returns an error message as a string.

    Example usage:
    result = get_hermes_keys()
    if isinstance(result, dict):
        print(f"Username: {result['username']}, Password: {result['password']}")
    else:
        print(result)  # This would print an error message.
    
    Raises:
    - requests.exceptions.RequestException: If there is any issue with the request (e.g., connection error, timeout).
    """
    
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
