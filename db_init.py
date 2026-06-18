import os
import psycopg2
from config import ADMIN_DB_CONFIG, DB_CONFIG, get_connection

def read_sql_file(filename):
    """Helper to read SQL files from the sql/ directory."""
    # Build path relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "sql", filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def create_database():
    """Drops and recreates the university_db database."""
    print("Connecting to administrative database 'postgres' to setup 'university_db'...")
    conn = get_connection(ADMIN_DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    
    dbname = DB_CONFIG["dbname"]
    
    print(f"Dropping database '{dbname}' if it exists...")
    cursor.execute(f"DROP DATABASE IF EXISTS {dbname};")
    
    print(f"Creating database '{dbname}'...")
    cursor.execute(f"CREATE DATABASE {dbname};")
    
    cursor.close()
    conn.close()
    print("Database creation complete.")

def create_tables():
    """Reads and executes sql/schema.sql."""
    print("Applying schema (sql/schema.sql)...")
    schema_sql = read_sql_file("schema.sql")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(schema_sql)
        conn.commit()
        print("Schema applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error applying schema: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def create_indexes():
    """Reads and executes sql/indexes.sql."""
    print("Creating indexes (sql/indexes.sql)...")
    indexes_sql = read_sql_file("indexes.sql")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(indexes_sql)
        conn.commit()
        print("Indexes created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error creating indexes: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def create_triggers():
    """Reads and executes sql/triggers.sql."""
    print("Creating triggers and functions (sql/triggers.sql)...")
    triggers_sql = read_sql_file("triggers.sql")
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(triggers_sql)
        conn.commit()
        print("Triggers and functions created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error creating triggers: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def initialize_all():
    """Orchestrates the entire database setup sequence."""
    print("=== STARTING DATABASE INITIALIZATION ===")
    try:
        create_database()
        create_tables()
        create_indexes()
        create_triggers()
        print("=== DATABASE INITIALIZATION COMPLETED SUCCESSFULY ===")
        return True
    except Exception as e:
        print(f"\nFailed to initialize database: {e}")
        return False

if __name__ == "__main__":
    initialize_all()





