import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT)
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT"),
    )
