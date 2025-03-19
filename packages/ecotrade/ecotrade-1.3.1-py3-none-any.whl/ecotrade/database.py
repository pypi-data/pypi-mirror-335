import requests
from ecotrade.utils import requires_auth

@requires_auth
def get_connection_string_db(db_type):
    """
    Retrieves the connection string for the specified database type.

    Parameters:
        - type (str): The type of database connection to retrieve. 
                      Acceptable values are:
                      - "DEAL" for the test database connection.
                      - "POW" for the power database connection.
                      - "PICO" for the PicoSystem database connection.
                      - "PROD_ETMS" for the ETMS production database connection.

    Returns:
        - str: The connection string for the specified database type.

    Example usage:
        - To get the connection string for the DEAL database:
          connection = get_connection_string_db("DEAL")
        
        - To get the connection string for the POW database:
          connection = get_connection_string_db("POW")
          
        - To get the connection string for the Pico database:
          connection = get_connection_string_db("PICO")

        - To get the connection string for the ETMS Production database:
          connection = get_connection_string_db("PROD_ETMS")
          
    Note:
        - Ensure the connection variables (e.g., `connection_pico`, `connection_prod_etms`, `connection_deal`, `connection_pow`) 
          are properly defined and accessible in the script before calling this function.
    """
    
    try:
        api_url = f"https://192.168.5.35:8080/get_db_connection_strings/{db_type}"

        response = requests.get(api_url, verify=False) 
        
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return f"Error during API call: {str(e)}"