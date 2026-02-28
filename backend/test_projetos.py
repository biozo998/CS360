import traceback
import logging
from unittest.mock import patch
from services.etl_engine import ETLEngine

logging.basicConfig(level=logging.INFO)

try:
    with patch('time.sleep', return_value=None):
        print("Starting Projetos Sync Test...")
        ETLEngine().sync_projetos()
        print("Success without error")
except Exception as e:
    with open('error_projetos.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    print("Error written to error_projetos.txt")
