import requests
from config import config

url = config.PSOFFICE_API_URL + '/api/rest/projeto'
headers = {'Authorization': f'Bearer {config.PSOFFICE_API_TOKEN}', 'Content-Type': 'application/json'}
res = requests.get(url, headers=headers, params={'view': 'EXTENDED', 'index': 8000})
data = res.json()

if isinstance(data, dict) and "info" in data and data["info"] is not None:
    print(f"Total Count Reported: {data['info'].get('count')}")
    print(f"Next Page Exists: {data['info'].get('next')}")
    print(f"Items on this page: {len(data['info'].get('itens', []))}")
else:
    print("NO INFO BLOCK OR NOT A DICT")
    print(list(data.keys()) if isinstance(data, dict) else type(data))
