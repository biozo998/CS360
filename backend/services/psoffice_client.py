import requests
import logging
import time
from config import config

logger = logging.getLogger(__name__)

def fix_recursive_encoding(data):
    if isinstance(data, dict):
        return {k: fix_recursive_encoding(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [fix_recursive_encoding(v) for v in data]
    elif isinstance(data, str):
        try:
            return data.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return data
    return data

class PSOfficeClient:
    def __init__(self):
        self.base_url = config.PSOFFICE_API_URL
        self.token = config.PSOFFICE_API_TOKEN
        
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, params=None):
        base = self.base_url.rstrip('/')
        param_path = endpoint.lstrip('/')
        url = f"{base}/{param_path}"
        
        if params is None:
            params = {}
            
        delay_seconds = 600 # 10 min
        max_retries = 3
        
        all_results = []
        has_next_page = True
        
        # We start at index 0 explicitly to allow auto-pagination
        if method.upper() == "GET" and "index" not in params:
            params["index"] = 0
            
        while has_next_page:
            logger.info(f"[PSOfficeClient] Requesting: {url} | Params: {params}")
            for attempt in range(max_retries + 1):
                try:
                    res = requests.request(method, url, headers=self.get_headers(), params=params)
                    
                    if res.status_code == 429:
                        logger.warning(f"[PSOfficeClient] 429 Too Many Requests. Waiting {delay_seconds//60} minutes... (Attempt {attempt+1})")
                        time.sleep(delay_seconds)
                        delay_seconds *= 2
                        continue
                        
                    res.raise_for_status()
                    data = fix_recursive_encoding(res.json())
                    
                    if isinstance(data, dict):
                        # Extract Items
                        if "info" in data and isinstance(data["info"], dict) and "itens" in data["info"]:
                            all_results.extend(data["info"]["itens"])
                            
                            # Check Pagination Flag
                            items_count = len(data["info"]["itens"])
                            if data["info"].get("next") is True and items_count > 0:
                                params["index"] = params.get("index", 0) + 1
                                delay_seconds = 600 # reset rate limit penalty timer
                                time.sleep(1.5) # inter-page delay to prevent WAF bot-detection
                                break # break the retry loop, but continue the while loop
                            else:
                                has_next_page = False
                                return all_results
                                
                        elif "content" in data and isinstance(data["content"], list):
                            return data["content"] # Assume non-paginated dictionary wrapper
                        elif "data" in data and isinstance(data["data"], list): 
                            return data["data"]
                        elif "items" in data and isinstance(data["items"], list): 
                            return data["items"]
                            
                    return data # Fallback if no pagination matches
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"[PSOfficeClient] API Error on {url}: {e}")
                    if hasattr(e, 'response') and e.response is not None:
                        logger.error(f"Response Body: {e.response.text}")
                    if attempt == max_retries:
                        raise e
                        
        return all_results
                
        raise Exception(f"[PSOfficeClient] Max retries exceeded for {url}")
            
    # --- Endpoints ---
    def get_apontamentos(self, data_inicio, data_fim, situacao=2):
        """
        Busca apontamentos no periodo.
        Ex: /api/v1/apontamentos/apontamentos?situacao=2&data_fim=05/01/2026&data_inicio=01/01/2026
        """
        params = {
            "situacao": situacao,
            "data_inicio": data_inicio,
            "data_fim": data_fim
        }
        return self._request("GET", "/api/v1/apontamentos/apontamentos", params=params)

    def get_projetos(self):
        return self._request("GET", "/api/rest/projeto", params={"view": "EXTENDED"})
        
    def get_atividades(self, proj_id):
        return self._request("GET", f"/api/rest/projeto/{proj_id}/atividades")

    def get_usuarios(self):
        return self._request("GET", "/api/rest/usuario")
        
    def get_clientes(self):
        return self._request("GET", "/api/rest/cliente")
