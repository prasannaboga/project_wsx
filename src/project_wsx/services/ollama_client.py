import requests


class OllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434"

    def post(self, path: str, payload: dict, timeout: int = 60) -> dict:
        api_url = f"{self.base_url}{path}"
        resp = requests.post(api_url, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
