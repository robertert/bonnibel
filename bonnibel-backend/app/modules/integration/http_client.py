import requests
import json
from typing import Dict, Any, Optional


class ExternalResponse:
    def __init__(self, status_code: int, text: str, json_data: Optional[Dict] = None):
        self.status_code = status_code
        self.text = text
        self._json = json_data

    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> Dict[Any, Any]:
        if self._json is None:
            self._json = json.loads(self.text) if self.text else {}
        return self._json


class IntegrationHttpClient:
    def get(self, url: str, token: str, params: Optional[Dict] = None) -> ExternalResponse:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        return ExternalResponse(resp.status_code, resp.text, resp.json() if resp.ok else None)

    def post(self, url: str, token: str, body: Optional[Dict] = None) -> ExternalResponse:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        resp = requests.post(url, headers=headers, json=body, timeout=20)
        return ExternalResponse(resp.status_code, resp.text, resp.json() if resp.ok else None)

    def put(self, url: str, token: str, body: Optional[Dict] = None) -> ExternalResponse:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        resp = requests.put(url, headers=headers, json=body, timeout=20)
        return ExternalResponse(resp.status_code, resp.text, resp.json() if resp.ok else None)

    def delete(self, url: str, token: str) -> ExternalResponse:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.delete(url, headers=headers, timeout=20)
        return ExternalResponse(resp.status_code, resp.text)