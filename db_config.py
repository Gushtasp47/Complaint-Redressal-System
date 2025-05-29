import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

def get_db_connection():
    conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=SmartComplaints;"
    "Trusted_Connection=yes;"
    )

    return conn
