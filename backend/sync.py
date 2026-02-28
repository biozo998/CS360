import sys
import os
import time
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.etl_engine import ETLEngine

def main():
    print("Starting ETL Sync...")
    etl = ETLEngine()
    
    try:
        etl.sync_clientes()
        etl.sync_projetos() # Note: API requires proj_id for atividades, we will pull all atividades for all locally saved projetos
        
        # Sync all assignments for all known projects
        from database import get_db
        from models.integration import Projeto
        db = next(get_db())
        try:
            projs = db.query(Projeto).all()
            for p in projs:
                print(f"Waiting 3 seconds before fetching atividades for proj_id {p.proj_id}...")
                time.sleep(3)
                etl.sync_atividades(p.proj_id)
        finally:
            db.close()
            
        etl.sync_usuarios()
        
        # Apontamentos (Syncing last 30 days as an example default)
        data_fim = datetime.now().strftime("%d/%m/%Y")
        data_inicio = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
        etl.sync_apontamentos(data_inicio, data_fim)
        
        # Agile Data
        etl.sync_agile()
        
        # Identity link
        etl.sync_users_identity()
        
        print("Sync completed successfully.")
    except Exception as e:
        print(f"ETL Sync failed: {e}")

if __name__ == "__main__":
    main()
