import traceback
import logging
from unittest.mock import patch
from services.etl_engine import ETLEngine

logging.basicConfig(level=logging.ERROR)

try:
    with patch('time.sleep', return_value=None):
        ETLEngine().sync_atividades(1)
        with open('error_dump_123.txt', 'w', encoding='utf-8') as f:
            f.write("Success")
except Exception as e:
    with open('error_dump_123.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
