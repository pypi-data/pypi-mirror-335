import requests


class BaseHTTP:
    def post(self, url, data, headers=None):
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
            return None
