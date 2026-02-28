import logging
import requests
from config import config
from services.psoffice_client import PSOfficeClient

logging.basicConfig(level=logging.INFO)

print("--- RAW REQUEST ---")
url = config.PSOFFICE_API_URL + '/api/rest/cliente'
headers = {'Authorization': f'Bearer {config.PSOFFICE_API_TOKEN}', 'Content-Type': 'application/json'}
print(f"Token length: {len(config.PSOFFICE_API_TOKEN)}")
res1 = requests.get(url, headers=headers, params={'index': 0})
print("Raw Status:", res1.status_code)

print("\n--- PSOfficeClient REQUEST ---")
try:
    c = PSOfficeClient()
    # We override sleep so it doesn't hang
    import time
    time.sleep = lambda x: print(f"Mock sleep {x}s")
    res2 = c.get_clientes()
    print("PSOfficeClient Result Length:", len(res2))
except Exception as e:
    print("PSOfficeClient Error:", e)
