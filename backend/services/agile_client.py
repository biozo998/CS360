import requests
import time
import logging
from config import config

logger = logging.getLogger(__name__)

class AgileClient:
    def __init__(self):
        env_url = config.AGILE_API_URL
        if "api.agile.psofficeapp.com.br" in env_url:
            self.base_url = "https://pso-csintegra.jexperts.cloud"
        else:
            self.base_url = env_url
            
        env_oauth = config.AGILE_OAUTH_URL
        if not env_oauth or "api.agile.psofficeapp.com.br" in str(env_oauth):
            self.oauth_url = "https://pso-csintegra.jexperts.cloud/api/oauth/token"
        else:
            self.oauth_url = env_oauth
            
        self.client_id = config.AGILE_CLIENT_ID
        self.client_secret = config.AGILE_CLIENT_SECRET
        
        self._access_token = None
        self._token_expires_at = 0
        
    def _get_access_token(self):
        """Fetches a new access token from the OAuth endpoint."""
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.oauth_url, headers=headers, data=data)
            response.raise_for_status()
            token_response = response.json()
            
            self._access_token = token_response.get('access_token')
            expires_in = token_response.get('expires_in', 600) # Defaults to 10 min if not provided
            
            # Set expiration time (current time + expires_in seconds minus a 30s safety margin)
            self._token_expires_at = time.time() + expires_in - 30
            
            logger.info("AgileClient: New access token acquired.")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"AgileClient Error fetching token: {e}")
            raise

    def get_headers(self):
        """Returns headers with a valid authentication token."""
        if not self._access_token or time.time() > self._token_expires_at:
            self._get_access_token()
            
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, params=None):
        base = self.base_url.rstrip('/')
        param_path = endpoint.lstrip('/')
        url = f"{base}/{param_path}"
        logger.info(f"[AgileClient] Requesting: {url}")
        
        delay_seconds = 600 # 10 min
        max_retries = 3
        
        for attempt in range(max_retries + 1):
            try:
                res = requests.request(method, url, headers=self.get_headers(), params=params)
                
                if res.status_code == 429:
                    logger.warning(f"[AgileClient] 429 Too Many Requests. Waiting {delay_seconds//60} minutes... (Attempt {attempt+1})")
                    time.sleep(delay_seconds)
                    delay_seconds *= 2
                    continue
                
                res.raise_for_status()
                
                data = res.json()
                if isinstance(data, dict):
                    if "data" in data: return data["data"]
                    if "items" in data: return data["items"]
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"[AgileClient] API Error on {url}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    logger.error(f"Response Body: {e.response.text}")
                raise
                
        raise Exception(f"[AgileClient] Max retries exceeded for {url}")

    # --- Endpoints ---
    def get_projects(self):
        return self._request("GET", "/psoffice-agile-api/agileprojects")
        


    def get_sprints(self):
        return self._request("GET", "/psoffice-agile-api/sprints")

    def get_users(self):
        return self._request("GET", "/psoffice-agile-api/users")
        
    def get_bucket_issues(self, agile_project_id):
        return self._request("GET", f"/psoffice-agile-api/bucketsissues", params={"agileProjectIds": agile_project_id})
        
    def get_issues(self, agile_project_id):
        return self._request("GET", f"/psoffice-agile-api/issues", params={"agileProjectIds": agile_project_id})
