#!/usr/bin/env python3
"""
Migration script to update location values in the database from old region codes to new city names.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import engine, SessionLocal
from app.models.transport import Transport
from app.models.user import User
from app.models.chat import Conversation
from sqlalchemy.orm import Session

LOCATION_MAPPING = {
    "tdk": "taldykorgan",
    "ala": "almaty",
    "ast": "astana",
    "shym": "shymkent",
    "atr": "atyrau"
}

def update_locations():
    """Update location values for all transports in the database."""
    db = SessionLocal()
    try:
        transports = db.query(Transport).all()
        
        updated_count = 0
        for transport in transports:
            old_location = transport.location
            if old_location in LOCATION_MAPPING:
                transport.location = LOCATION_MAPPING[old_location]
                updated_count += 1
        
        db.commit()
        print(f"Successfully updated {updated_count} transport locations.")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating locations: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting location value migration...")
    update_locations()
    print("Location migration completed.") 