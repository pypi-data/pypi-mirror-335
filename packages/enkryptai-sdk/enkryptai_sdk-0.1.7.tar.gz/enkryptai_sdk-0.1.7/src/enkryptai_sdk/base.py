import urllib3
from typing import Dict, Any


class BaseClient:
    def __init__(self, api_key: str, base_url: str = "https://api.enkryptai.com"):
        if api_key is None:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.http = urllib3.PoolManager()
        self.headers = {"apikey": self.api_key}

    def _request(self, method, endpoint, payload=None, headers=None, **kwargs):
        url = self.base_url + endpoint
        request_headers = {
            "Accept-Encoding": "gzip",  # Add required gzip encoding
            **self.headers,
        }
        if headers:
            request_headers.update(headers)

        try:
            response = self.http.request(method, url, headers=request_headers, **kwargs)

            if response.status >= 400:
                error_data = (
                    response.json()
                    if response.data
                    else {"message": f"HTTP {response.status}"}
                )
                error_message = error_data.get("message", str(error_data))
                raise urllib3.exceptions.HTTPError(error_message)
            return response.json()
        except urllib3.exceptions.HTTPError as e:
            return {"error": str(e)}
