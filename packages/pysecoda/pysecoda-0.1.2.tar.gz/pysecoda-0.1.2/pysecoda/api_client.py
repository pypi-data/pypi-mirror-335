import requests

class APIClient:
    """
    A simple Python wrapper for making API requests with Bearer authentication.
    """
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initializes the API client.
        
        :param base_url: Base URL of the API.
        :param api_key: Bearer token for authentication.
        """
        self.__base_url = base_url.rstrip('/')
        self.__headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_base_url(self):
        return self.__base_url

    def _request(self, method: str, endpoint: str, params=None, data=None):
        """
        Internal method to send HTTP requests.
        
        :param method: HTTP method (GET, POST, etc.).
        :param endpoint: API endpoint.
        :param params: Dictionary of URL parameters.
        :param data: Dictionary of JSON payload.
        :return: Response JSON or raises an error.
        """
        url = f"{self.__base_url}/{endpoint.lstrip('/')}"

        print(url)

        response = requests.request(method, url, headers=self.__headers, params=params, json=data)
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise Exception(f"API request failed: {err}")
    
    def get(self, endpoint: str, params=None):
        """Sends a GET request."""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data=None):
        """Sends a POST request."""
        return self._request("POST", endpoint, data=data)
    
    def patch(self, endpoint: str, data=None):
        """Sends a PUT request."""
        return self._request("PATCH", endpoint, data=data)
    
    def delete(self, endpoint: str):
        """Sends a DELETE request."""
        return self._request("DELETE", endpoint)
