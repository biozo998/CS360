import traceback
from services.etl_engine import ETLEngine

try:
    print("Starting sync_usuarios...")
    ETLEngine().sync_usuarios()
    print("Success syncing Usuarios")
except Exception as e:
    with open('error_usuarios.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    print("Failed. Check error_usuarios.txt")
