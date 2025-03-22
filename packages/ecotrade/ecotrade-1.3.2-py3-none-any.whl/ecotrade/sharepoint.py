import msal
import requests
import pandas as pd
import json
from io import BytesIO
from ecotrade.utils import requires_auth

TENANT_ID = ""
CLIENT_ID = ""
CLIENT_SECRET = ""
SITE_ID = ""
DRIVER_ID = ""

@requires_auth
def open_session_msc():
    """
    Fetches the Microsoft credentials from the specified API endpoint and assigns them to global variables.
    """
    global TENANT_ID, CLIENT_ID, CLIENT_SECRET, SITE_ID, DRIVER_ID 

    try:
        api_url = "https://192.168.5.35:8080/get_microsoft_credentials"
        response = requests.get(api_url, verify=False)
        
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"
        
        result = response.json()
        
        if "TENANT_ID" in result and "CLIENT_ID" in result and "CLIENT_SECRET" in result and "SITE_ID" in result and "DRIVER_ID" in result:
            TENANT_ID = result["TENANT_ID"]
            CLIENT_ID = result["CLIENT_ID"]
            CLIENT_SECRET = result["CLIENT_SECRET"]
            SITE_ID = result["SITE_ID"]
            DRIVER_ID = result["DRIVER_ID"]
            return "Variables and Microsoft session set successfully!"
        else:
            return "Failed to retrieve credentials: Missing some required data in response"
    
    except requests.exceptions.RequestException as e:
        return f"Error during API call: {str(e)}"

# Microsoft API authentication
@requires_auth
def microsoft_auth():
    open_session_msc()
    """
    Acquires an OAuth2.0 access token from Microsoft Identity Platform to authenticate
    against the Microsoft Graph API using client credentials.

    Parameters:
        - TENANT_ID: The tenant ID in Azure Active Directory.
        - CLIENT_ID: The client/application ID registered in Azure Active Directory.
        - CLIENT_SECRET: The client secret for authenticating the app in Azure AD.

    Returns:
        - access_token (str): A valid access token to authenticate API requests against Microsoft Graph.
        
    Raises:
        - Exits the script with an error message if the token acquisition fails.
    """
    global TENANT_ID, CLIENT_ID, CLIENT_SECRET

    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    
    app = msal.ConfidentialClientApplication(
        client_id=CLIENT_ID, 
        client_credential=CLIENT_SECRET, 
        authority=authority
    )
    
    scopes = ["https://graph.microsoft.com/.default"]
    
    result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        access_token = result["access_token"]
        return access_token
    else:
        print("Failed to acquire token:", result.get("error_description", "Unknown error"))
        exit(1)

# Get all the GENERAL folders contents
@requires_auth
def get_general_folder_content_list():
    """
    Retrieves and displays the contents of the Ecotrade GENERAL folder.

    Functionality:
        - Authenticates with Microsoft Graph API.
        - Fetches the contents of the given folder.
        - Identifies whether each item is a file or a folder.
        - Prints the name, type (File/Folder), and ID of each item.

    Returns:
        - None (prints folder details to the console).
    """
    global SITE_ID, DRIVER_ID  # Access global variables

    access_token = microsoft_auth()
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    GENERAL_FOLDER = "01JJVAJCGGNPD6F7EBJVHL64KD3FWCEYFX"
    folder_url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVER_ID}/items/{GENERAL_FOLDER}/children"
    response = requests.get(folder_url, headers=headers)
    if response.status_code == 200:
        items = response.json().get("value", [])
        if items:
            print(f"Contents of folder 'General' (ID: {DRIVER_ID}):")
            for item in items:
                item_type = "File" if "file" in item else "Folder"
                print(
                    f"Item Name: {item['name']}, Item Type: {item_type}, Item ID: {item['id']}"
                )
        else:
            print("No items found in this folder.")
    else:
        print(f"Failed to retrieve contents of folder: {response.status_code}")
        print(response.text)

# Find a specific Excel file
@requires_auth
def find_excel_file(FOLDER_ID):
    """
    Searches for an Excel (.xlsx) file in the given folder and returns its key details.

    Parameters:
        - FOLDER_ID: OneDrive/SharePoint identifiers.
        
    Returns:
        - Dictionary with file details if found, otherwise None.
    """
    global SITE_ID, DRIVER_ID 

    access_token = microsoft_auth()
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    folder_url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVER_ID}/items/{FOLDER_ID}/children"
    response = requests.get(folder_url, headers=headers)

    if response.status_code == 200:
        folders = response.json().get("value", [])

        for item in folders:
            if item["name"].endswith(".xlsx"):
                file_details = {
                    "name": item["name"],
                    "id": item["id"],
                    "size": item.get("size", "Unknown"),
                    "lastModifiedDateTime": item.get("lastModifiedDateTime", "Unknown"),
                    "createdBy": item.get("createdBy", {})
                    .get("user", {})
                    .get("displayName", "Unknown"),
                    "downloadUrl": item.get(
                        "@microsoft.graph.downloadUrl", "Unavailable"
                    ),
                }
                print(json.dumps(file_details, indent=4))
                return file_details

        print("No Excel file found in the folder.")
        return None

    else:
        print(f"Failed to retrieve folder contents: {response.status_code}")
        print(response.text)
        return None

# Read the content of a specific excel file
@requires_auth
def read_excel_file(FILE_ID):
    """
    Reads the Excel file from Microsoft Graph API using its file ID.

    Parameters:
        - FILE_ID: ID of the Excel file.
        
    Returns:
        - A Pandas DataFrame containing the file's content.
    """
    if not FILE_ID:
        print("Invalid file ID.")
        return None

    global SITE_ID, DRIVER_ID

    access_token = microsoft_auth()
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    download_url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVER_ID}/items/{FILE_ID}/content"
    download_response = requests.get(download_url, headers=headers)

    if download_response.status_code == 200:
        df = pd.read_excel(BytesIO(download_response.content))
        pd.set_option('display.max_rows', None)  
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        print(f"Successfully read the file with ID: {FILE_ID}")
        print("File contents:")
        return df
    else:
        print(f"Failed to read the file: {download_response.status_code}")
        print(download_response.text)
        return None

