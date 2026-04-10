import requests
import logging
from config.settings import config

logger = logging.getLogger(__name__)


class ApiClient:
    """API请求客户端封装"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.base_url = config.BASE_URL
        self.timeout = config.TIMEOUT

    def _log_request(self, method, url, **kwargs):
        logger.info(f"Request: {method} {url}")
        if "json" in kwargs:
            logger.debug(f"Request Body: {kwargs['json']}")

    def _log_response(self, response):
        logger.info(f"Response: {response.status_code}")
        logger.debug(f"Response Body: {response.text[:500]}")

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)

        self._log_request(method, url, **kwargs)

        try:
            response = self.session.request(method, url, **kwargs)
            self._log_response(response)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get(self, endpoint, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)

    def set_auth_token(self, token):
        """设置认证Token"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def close(self):
        self.session.close()