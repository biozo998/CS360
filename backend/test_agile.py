from database import init_db
from services.etl_engine import ETLEngine
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Starting sync_agile...")
    init_db()
    engine = ETLEngine()
    engine.sync_agile()
    print("Success syncing Agile!")
