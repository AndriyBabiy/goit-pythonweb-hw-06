import os
import pprint
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from config import DATABASE_URL, DB_HOST, DB_PORT

def check_db_connection():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("✅ Connection to postgres successful!")
            query = text("SELECT version();")
            result = connection.execute(query)
            db_version = result.scalar_one()
            print(f"PostgreSQL version: {db_version}")

    except OperationalError as e:
        print(f"❌ Could not connect to the database. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred. Error: {e}")


if __name__ == "__main__":
    print(f"SQLAlchemy version: {sqlalchemy.__version__}")
    print(f"Attempting to connect to: {DB_HOST}:{DB_PORT}...")
    check_db_connection()
