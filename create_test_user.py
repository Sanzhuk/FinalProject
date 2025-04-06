import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to the database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agritransport.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_user():
    """Create a test user account if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if the test user already exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if test_user:
            print("Test user already exists!")
            return test_user
        
        # Create a new test user
        hashed_password = get_password_hash("password123")
        new_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=hashed_password,
            is_active=True,
            is_owner=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("Test user created successfully!")
        print("Email: test@example.com")
        print("Password: password123")
        return new_user
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 