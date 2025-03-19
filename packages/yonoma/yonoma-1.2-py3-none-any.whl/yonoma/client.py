import requests
from yonoma.exceptions import YonomaAPIError
from yonoma.version import VERSION

class YonomaClient:
    BASE_URL = "https://api.yonoma.io/v1/"

    def __init__(self, api_key):
        self.api_key = api_key 
        self.version = VERSION  
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"yonoma-python: {self.version}"
        }

    def request(self, method, endpoint, data=None):
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(method, url, json=data, headers=self.headers)
        if response.status_code >= 400:
            raise YonomaAPIError(response.json())
        return response.json()
    
