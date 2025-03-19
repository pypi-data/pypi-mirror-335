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
    
    db_connections = {
        "PICO": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=picosys.westeurope.cloudapp.azure.com,1437;DATABASE=USER_ECOTRADE;UID=ecotrade;PWD=v5V4sZGjFjuw3saqJIuO",
        "PROD_ETMS": "DRIVER={SQL Server};SERVER=192.168.5.35\SQLEXPRESS;DATABASE=ETMS_Production;UID=deal;PWD=deal2023!",
        "DEAL": "DRIVER={SQL Server};SERVER=192.168.5.35\SQLEXPRESS;DATABASE=deal;UID=deal;PWD=deal2023!",
        "POW": "DRIVER={SQL Server};SERVER=192.168.5.35\SQLEXPRESS;DATABASE=POW;UID=deal;PWD=deal2023!",
    }

    connection = db_connections.get(db_type)
    if connection is None:
        raise ValueError(f"Invalid database type: {db_type}")
    return connection