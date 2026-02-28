import sys
import os

# Ensure backend root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
import models # Imports __init__.py which has all models

def init_db():
    print("[Database] Warning: Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("[Database] Creating all tables from SQLAlchemy models...")
    Base.metadata.create_all(bind=engine)
    print("[Database] Initialization complete.")

if __name__ == "__main__":
    init_db()
