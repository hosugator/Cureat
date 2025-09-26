#!/usr/bin/env python3
"""
Database update script to recreate tables with new schema
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.database import engine, Base
from app import models

def update_database():
    """Update database schema"""
    print("Updating database schema...")
    
    # Drop and recreate all tables to ensure schema is correct
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print("Database updated successfully with new schema including operating_hours field")

if __name__ == "__main__":
    update_database()