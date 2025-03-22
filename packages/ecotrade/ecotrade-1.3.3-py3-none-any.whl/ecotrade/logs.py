from ecotrade.authentication import Auth
from ecotrade.utils import requires_auth
from pymongo import MongoClient
from datetime import datetime
from ecotrade.database import get_connection_string_db

@requires_auth
def save_logs(unique_identifier, log_type, log_message):
    """
    Saves logs in logs collection

    Parameters:
        - unique_identifier: A custom identifier.
        - log_type: The type of log.
        - message: The log message.
    
    Acceptable values for log_type are:
        - "SUCCESS" for success cases.
        - "ERROR" for error cases.
        - "WARNING" for warning cases.
        
    Acceptable values for unique_identifier are: any
    Acceptable values for log_message are: any

    Returns:
        - dict: Status and function message.

    Example usage:
        - To save a SUCCESS log : error = save_logs("SUCCESS", "This is a success log")
        
        - To save an ERROR log : error = save_logs("ERROR", "This is an error log")
        
        - To save a WARNING log : warning = save_logs("WARNING", "This is a warning log")
          
    Note:
        - Ensure the log_type variables (e.g., `SUCCESS`, `ERROR`, `WARNING`) 
          are properly defined and accessible in the script before calling this function.
    """

    if log_type != "ERROR" and log_type != "SUCCESS" and log_type != "WARNING":
        return {"status": "KO", "message": "Log type is incorrect - Only SUCCESS, ERROR ot WARNING allowed"}
    
    current_datetime = datetime.now().isoformat()
    data = {
        "user": Auth._authenticated_user,
        "unique_identifier": unique_identifier, 
        "log_type": log_type,
        "log_message": log_message,
        "timestamp":  current_datetime
    }
    
    try:
        uri = get_connection_string_db("MONGO")
        client = MongoClient(uri["connection_string"])
        db = client["ecotrade"]
        logs_collection = db["logs"]
        logs_collection.insert_one(data)
        return {"status": "OK", "message": "Log saved successfully"}
    except Exception as e:
        return ({"status": "KO", "message": "Something went wrong during save_log"})
    
    
def get_logs(query):
    """
    Retrieves logs from the 'logs' collection in the MongoDB database based on the provided query,
    ensuring that only logs related to the authenticated user are returned.

    The function uses the authenticated user's information to filter logs by the 'user' field 
    in the MongoDB collection. It then fetches logs based on the combined query and returns 
    the result, excluding the MongoDB default '_id' field.

    Args:
        query (dict): A dictionary representing the filter conditions to query the logs. The query 
                      is automatically modified to include the authenticated user's information.

    Returns:
        dict: A response dictionary containing the status, logs, query, and a message. 
              If logs are found, they are returned under the "logs" key. If no logs are found, 
              a "No logs found" message is returned. In case of an error, an error message is returned.

    Example:
        query = {"action": "login"}
        result = get_logs(query)
        print(result)

    @raises:
        Exception: If any issue occurs during the connection to the database or fetching of logs.
    """
    try:
        uri = get_connection_string_db("MONGO")
        client = MongoClient(uri["connection_string"])
        db = client["ecotrade"]
        logs_collection = db["logs"]

        user = Auth._authenticated_user  
        query["user"] = user
        logs = list(logs_collection.find(query, {"_id": 0}))

        return {"status": "OK", "logs": logs, "query": query} if logs else {"status": "OK", "query": query, "message": "No logs found"}

    except Exception as e:
        return {"status": "KO", "message": f"Something went wrong during the get_logs"}
