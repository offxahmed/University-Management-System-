import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection configuration
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "ehmed"),
    "dbname": os.environ.get("DB_NAME", "university_db")
}

# Configuration for administrative tasks (like dropping/creating the database)
# Points to the default 'postgres' database
ADMIN_DB_CONFIG = DB_CONFIG.copy()
ADMIN_DB_CONFIG["dbname"] = "postgres"

def get_connection(config=None):
    """
    Establishes and returns a connection to the PostgreSQL database.
    If no config is provided, uses the default DB_CONFIG.
    """
    if config is None:
        config = DB_CONFIG
    
    return psycopg2.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["dbname"]
    )
