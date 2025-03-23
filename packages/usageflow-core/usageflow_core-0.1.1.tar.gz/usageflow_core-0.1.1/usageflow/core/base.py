import requests
import jwt
import threading
import time
from typing import Dict, Any, Optional, Tuple

class UsageFlowClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.usageflow_url = "https://api.usageflow.io"
        self.api_config = None
        self.lock = threading.Lock()
        self.start_config_updater()

    def start_config_updater(self):
        """Background thread to periodically fetch API configuration"""
        def update_config():
            while True:
                try:
                    config = self.fetch_api_config()
                    if config:
                        with self.lock:
                            self.api_config = config
                            print("config", self.api_config)
                except Exception as e:
                    print(f"Error fetching API config: {e}")
                
                time.sleep(30)  # Refresh every 30 seconds

        thread = threading.Thread(target=update_config, daemon=True)
        thread.start()

    def fetch_api_config(self) -> Dict[str, Any]:
        """Fetch API configuration from UsageFlow"""
        url = f"{self.usageflow_url}/api/v1/strategies/application"
        headers = {"x-usage-key": self.api_key, "Content-Type": "application/json"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch API config: {response.text}")

    def allocate_request(self, ledger_id: str, metadata: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Allocate usage for a request"""
        print("self.usageflow_url", self.usageflow_url)
        api_url = f"{self.usageflow_url}/api/v1/ledgers/measure/allocate"
        
        headers = {
            "x-usage-key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "alias": ledger_id,
            "amount": 1,
            "metadata": metadata,
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            response_data = response.json()

            if 200 <= response.status_code < 300:
                return True, response_data
            
            return False, response_data

        except requests.Timeout:
            return False, {"error": "Request timed out"}
        except requests.ConnectionError:
            return False, {"error": "Service unavailable"}
        except requests.RequestException as e:
            return False, {"error": str(e)}

    def fulfill_request(self, ledger_id: str, allocation_id: str, metadata: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Fulfill the request by finalizing usage"""
        api_url = f"{self.usageflow_url}/api/v1/ledgers/measure/allocate/use"
        
        headers = {
            "x-usage-key": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "alias": ledger_id,
            "amount": 1,
            "allocationId": allocation_id,
            "metadata": metadata,
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            return response.status_code >= 200 and response.status_code < 300, response.json()
        except requests.RequestException:
            return True, None

    def extract_bearer_token(self, auth_header: Optional[str]) -> Optional[str]:
        if not auth_header:
            return None
        parts = auth_header.split()
        return parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else None

    def decode_jwt_unverified(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError:
            return None

    def transform_to_ledger_id(self, identifier: str) -> str:
        """Transform an identifier to a ledger ID format"""
        return str(identifier)

    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get the current API configuration"""
        with self.lock:
            return self.api_config

    def log_response(self, metadata: Dict[str, Any]) -> None:
        """Log the response details"""
        requests.post(
            f"{self.usageflow_url}/api/v1/strategies/log",
            json=metadata,
            headers={"x-usage-key": self.api_key, "Content-Type": "application/json"}
        ) 