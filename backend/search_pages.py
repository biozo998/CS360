import requests
from config import config

url = config.PSOFFICE_API_URL + '/api/rest/projeto'
headers = {'Authorization': f'Bearer {config.PSOFFICE_API_TOKEN}', 'Content-Type': 'application/json'}

def check_page(index):
    res = requests.get(url, headers=headers, params={'view': 'EXTENDED', 'index': index})
    data = res.json()
    if isinstance(data, dict) and "info" in data and data["info"] is not None:
        count = len(data["info"].get("itens", []))
        return count
    return 0

low = 0
high = 2000
last_valid = 0

print(f"Executing binary search to find last project page...")
while low <= high:
    mid = (low + high) // 2
    count = check_page(mid)
    print(f"Checked page {mid}: {count} items")
    if count > 0:
        last_valid = mid
        low = mid + 1
    else:
        high = mid - 1

print(f"\\nFINAL RESULT: The last valid page is {last_valid}")
print(f"Total projects approximate: {last_valid * 100}")
