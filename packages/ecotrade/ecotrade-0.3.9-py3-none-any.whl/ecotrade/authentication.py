import os
import pyodbc
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

class Auth:
    _authenticated = False

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password.encode("utf-8")

        # Fetch database credentials from environment variables
        db_driver = os.getenv("DB_DRIVER", "{SQL Server}")
        db_server = os.getenv("DB_SERVER", "your_server")
        db_name = os.getenv("DB_NAME", "your_database")
        db_user = os.getenv("DB_USER", "your_user")
        db_password = os.getenv("DB_PASSWORD", "your_password")

        self.db_conn_string = f"DRIVER={db_driver};SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_password}"

    def authenticate(self):
        try:
            conn = pyodbc.connect(self.db_conn_string)  # Connect to the database
            cursor = conn.cursor()

            query = "SELECT password FROM [ETMS_Production].[dbo].[etms_users] WHERE email = ?"
            cursor.execute(query, (self.email,))
            result = cursor.fetchone()

            if not result:
                return "Failed to authenticate: User not found"

            stored_hashed_password = result[0]

            if isinstance(stored_hashed_password, bytes):
                stored_hashed_password = stored_hashed_password.decode("utf-8")

            if bcrypt.checkpw(self.password, stored_hashed_password.encode("utf-8")):
                Auth._authenticated = True
                conn.close()
                return "Authentication successful"
            else:
                conn.close()
                return "Failed to authenticate: Incorrect password"

        except Exception as e:
            return f"Error during authentication: {str(e)}"
