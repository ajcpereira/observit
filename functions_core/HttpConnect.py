import logging
import requests
import urllib3

class HttpConnect:
    def __init__(self, base_url, username=None, password=None, unsecured=False):
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)
        self.base_url = base_url
        self.unsecured = unsecured

        logging.debug(f"Received parameters: base_url={base_url}, username={username}, unsecured={unsecured}")

        if self.unsecured:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get(self, endpoint, headers=None):
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, headers=headers, verify=not self.unsecured)
            response.raise_for_status() # Raise an exception if status code indicates an error
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return None

    def post(self, endpoint, data=None, headers=None):
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(url, json=data, headers=headers, verify=not self.unsecured) # Including headers in request
            response.raise_for_status() # Raise an exception if status code indicates an error
            return response
        except requests.RequestException as e:
            logging.error(f"Error posting data to {url}: {e}")
            return None

    def close(self):
        self.session.close()
