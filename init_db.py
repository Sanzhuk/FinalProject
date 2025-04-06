import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.db.database import Base, engine
from app.models import user, transport
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
        return True
    except OperationalError as e:
        print(f"Error: Could not connect to the database. Make sure PostgreSQL is running.")
        print(f"Error details: {e}")
        return False

if __name__ == "__main__":
    try:
        success = init_db()
        if success:
            print("Database initialization complete.")
        else:
            print("Database initialization failed.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1) 