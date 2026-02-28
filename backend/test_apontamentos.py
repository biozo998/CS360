import traceback
from datetime import datetime
from services.etl_engine import ETLEngine

try:
    data_inicio = '01/01/2026'
    data_fim = datetime.now().strftime('%d/%m/%Y') # Gets today's date formatted
    
    print(f"Starting sync_apontamentos from {data_inicio} to {data_fim}...")
    ETLEngine().sync_apontamentos(data_inicio, data_fim)
    print("Success syncing Apontamentos")
    
except Exception as e:
    with open('error_apontamentos.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    print("Failed. Check error_apontamentos.txt")
