import requests
from config import config

url = "https://api.psofficeapp.com.br/csintegra/api/v1/apontamentos/apontamentos"
headers = {
    "Token": config.PSOFFICE_API_TOKEN,
    "Content-Type": "application/json"
}
params = {
    "situacao": 2,
    "data_inicio": "20/02/2026",
    "data_fim": "28/02/2026",
    "index": 0
}

found = False
for idx in range(5):
    params["index"] = idx
    r = requests.get(url, headers=headers, params=params)
    raw_bytes = r.content
    
    # search for 'Ã' (which is c3 83 in utf8, or \xc3 inside a latin string)
    # wait, 'Ã' encoded in utf8 is b'\xc3\x83'
    # 'ç' encoded in latin-1 is \xe7. But if the api sends "Ã§", it's sending b'\xc3\x83\xc2\xa7'
    # let's just search for 'olvida' (desenvolvida) or 'relat' (relatÃ³rio)
    pos = raw_bytes.find(b'relat')
    if pos == -1:
        pos = raw_bytes.find(b'A\xc3\xa7\xc3\xa3o') # Ação double encoded
    if pos == -1:
        pos = raw_bytes.find(b'parametriza')
        
    if pos != -1:
        found = True
        snippet = raw_bytes[pos:pos+40]
        print("RAW BYTES:", snippet)
        
        try:
            print("UTF-8 Decode:", snippet.decode('utf-8'))
        except:
            pass
            
        try:
            double_dec = snippet.decode('utf-8').encode('latin-1').decode('utf-8')
            print("DOUBLE DECODE:", double_dec)
        except Exception as e:
            print("Double decode error:", e)
        break

if not found:
    print("No accented words found in first 5 pages.")
