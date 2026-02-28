import traceback
import logging
import time
from unittest.mock import patch
from database import get_db
from models.integration import Projeto
from services.etl_engine import ETLEngine

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

try:
    with patch('time.sleep', return_value=None):
        logger.info("Starting Batch Sync for Atividades...")
        db = next(get_db())
        projetos = db.query(Projeto.proj_id).all()
        db.close()
        
        total = len(projetos)
        logger.info(f"Targeting {total} projects for Atividades Scan...")
        
        etl = ETLEngine()
        for i, (p_id,) in enumerate(projetos, 1):
            try:
                # Add tiny delay between projects to spread API load
                time.sleep(0.5)
                logger.info(f"[{i}/{total}] Syncing Atividade for Project ID {p_id}")
                etl.sync_atividades(p_id)
            except Exception as loop_e:
                logger.error(f"Failed to sync proj {p_id}: {loop_e}")
        
        logger.info("COMPLETED ALL ATIVIDADES")
except Exception as e:
    with open('error_atividades.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    print("FATAL ERROR written to error_atividades.txt")
