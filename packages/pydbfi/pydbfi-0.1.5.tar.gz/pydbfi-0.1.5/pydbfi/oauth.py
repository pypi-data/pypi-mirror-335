import logging
import threading
from datetime import datetime, timedelta

import requests


class OAuth:
    _instance = None
    _lock = threading.Lock()

    BASE_URL = "https://openapi.db-fi.com:8443"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(OAuth, cls).__new__(cls)
        return cls._instance

    def __init__(self, appkey: str, appsecretkey: str):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.appkey = appkey
        self.appsecretkey = appsecretkey
        self.token = None
        self.expire_in = None
        self.token_type = None
        self.logger = logging.getLogger(__name__)
        self._initialized = True

    def get_token(self) -> str:
        if not self.is_token_valid():
            with OAuth._lock:
                if not self.is_token_valid():
                    self.request_token()
        return self.token

    def is_token_valid(self) -> bool:
        if not self.token or not self.expire_in:
            return False
        return datetime.now() + timedelta(minutes=10) < self.expire_in

    def request_token(self) -> None:
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "appsecretkey": self.appsecretkey,
            "scope": "oob",
        }
        try:
            self.logger.info("Requesting new access token from DB Securities API")
            response = requests.post(
                f"{self.BASE_URL}/oauth2/token", headers=headers, data=data
            )
            response.raise_for_status()
            token_data = response.json()

            self.token = token_data.get("access_token")
            expire_in = int(token_data.get("expires_in", 86400))
            self.expire_in = datetime.now() + timedelta(seconds=expire_in)
            self.token_type = token_data.get("token_type")
            self.logger.info(
                f"New access token obtained. Valid until: {self.expire_in}"
            )
        except requests.RequestException as e:
            self.logger.error(f"Failed to obtain access token: {str(e)}")
            raise

    def revoke_token(self) -> dict:
        if not self.token:
            self.logger.warning("No token to revoke")
            return {"code": 400, "message": "No token to revoke"}

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "appkey": self.appkey,
            "appsecretkey": self.appsecretkey,
            "token": self.token,
            "token_type_hint": "access_token",
        }
        try:
            self.logger.info("Revoking access token")
            response = requests.post(
                f"{self.BASE_URL}/oauth2/revoke", headers=headers, data=data
            )
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 200:
                self.token = None
                self.expire_in = None
                self.token_type = None
                self.logger.info("Token successfully revoked")
            return result
        except requests.RequestException as e:
            self.logger.error(f"Failed to revoke token: {str(e)}")
            if hasattr(e, "response") and e.response:
                self.logger.error(f"Response: {e.response.text}")
            raise

    def get_auth_header(self) -> dict:
        return {"authorization": f"{self.token_type} {self.get_token()}"}
