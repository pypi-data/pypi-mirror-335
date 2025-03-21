import requests
from time import time, sleep
from typing import Optional
from lxml import html
from urllib.parse import urlparse, parse_qs
from time import sleep
import logging
from .logger import logger
from .InsulaAuthorizationApiConfig import InsulaAuthorizationApiConfig


class InsulaOpenIDConnect(InsulaAuthorizationApiConfig):
    def __init__(self, authorization_endpoint: str, token_endpoint: str, client_id: str, redirect_uri: str,
                 disable_ssl: bool = False, loglevel: str = 'INFO'):
        self.__client_id: str = client_id
        self.__redirect_uri: str = redirect_uri
        self.__authorization_endpoint: str = authorization_endpoint
        self.__token_endpoint: str = token_endpoint
        self.__token_type: str = 'Bearer'
        self.__scope: Optional[str] = 'openid'
        self.__client_secret: Optional[str] = None

        self.__username: Optional[str] = None
        self.__password: Optional[str] = None

        self.__init_token_time: int = 0
        self.__init_refresh_token_time: int = 0

        self.__refresh_token: Optional[str] = None
        self.__access_token: Optional[str] = None

        self.__expires_in = 0
        self.__refresh_expires_in = 0

        self.__session = requests.Session()
        if disable_ssl:
            self.__session.verify = False

        if loglevel == 'CRITICAL':
            logging.root.level = logging.CRITICAL
        if loglevel == 'ERROR':
            logging.root.level = logging.ERROR
        if loglevel == 'WARNING':
            logging.root.level = logging.WARNING
        if loglevel == 'INFO':
            logging.root.level = logging.INFO
        if loglevel == 'DEBUG':
            logging.root.level = logging.DEBUG

    def set_user_credentials(self, username: str, password: str):
        self.__username = username
        self.__password = password

    def get_authorization_header(self):
        if not self.__is_valid_token():
            attempt = 0
            while True:
                if attempt > 3:
                    raise RuntimeError('It is impossible to recover the token')
                try:
                    self._create_token()
                    break
                except Exception as e:
                    attempt += 1
                    sleep(2)

        return f'{self.__token_type} {self.__access_token}'

    def __is_refresh_token_valid(self, now) -> bool:
        return self.__init_refresh_token_time + self.__refresh_expires_in > now

    def __is_access_token_valid(self, now) -> bool:
        return self.__init_token_time + self.__expires_in > now

    def __is_valid_token(self) -> bool:

        now = time()

        if self.__init_token_time == 0 and self.__init_refresh_token_time == 0:
            return False

        if self.__is_access_token_valid(now):
            logger.debug('use token cache')
            return True

        if self.__is_refresh_token_valid(now):
            logger.debug('use refresh token cache')
            self.__retrieve_refresh_token_from_endpoint()
            return True

        logger.debug('refresh token not valid')
        return False

    def _create_token(self):
        logger.debug('create token')
        return self.__retrieve_token_from_endpoint(
            self.__retrieve_authorization_from_endpoint()
        )

    def __retrieve_authorization_from_endpoint(self) -> str:
        """
        Calls the authorization endpoint and returns 'code'
        """
        get_params = {
            "client_id": self.__client_id,
            "redirect_uri": self.__redirect_uri,
            "scope": "openid",
            "response_type": "code"
        }

        response_auth = self.__session.get(url=self.__authorization_endpoint, params=get_params)
        if response_auth.status_code != 200:
            self.__logs_and_raise('call authorization endpoint failed')

        auth_url = html.fromstring(response_auth.content.decode()).forms[0].action

        post_data = {
            "username": self.__username,
            "password": self.__password
        }

        response = self.__session.post(auth_url, data=post_data, allow_redirects=False)

        if response.status_code != 302:
            self.__logs_and_raise('Authorization failed, username or password incorrect [err: 199]')

        if 'Location' not in response.headers:
            self.__logs_and_raise('Authorization failed, username or password incorrect [err: 100]')

        return parse_qs(urlparse(response.headers['Location']).query)['code'][0]

    def __retrieve_token_from_endpoint(self, code: str) -> dict:
        post_data = {
            "client_id": self.__client_id,
            "redirect_uri": self.__redirect_uri,
            "code": code,
            "grant_type": "authorization_code"
        }

        logger.debug("retrieve token")
        return self.__get_token_from_server(post_data)

    def __retrieve_refresh_token_from_endpoint(self) -> dict:

        post_data = {
            "client_id": self.__client_id,
            "redirect_uri": self.__redirect_uri,
            "refresh_token": self.__refresh_token,
            "grant_type": "refresh_token"
        }

        logger.debug("retrieve from refresh token")
        return self.__get_token_from_server(post_data)

    def __get_token_from_server(self, data):
        response = self.__session.post(self.__token_endpoint, data=data)
        if response.status_code != 200:
            self.__logs_and_raise('Cannot retrieve token [err: 110]')
        return self.__parse_and_update_cache_token(response)

    def __parse_and_update_cache_token(self, response: requests.Response):
        _token = response.json()
        self.__access_token = _token['access_token']
        self.__refresh_token = _token['refresh_token']
        self.__token_type = _token['token_type']
        self.__expires_in = _token['expires_in']
        self.__refresh_expires_in = _token['refresh_expires_in']
        self.__init_token_time = time()
        self.__init_refresh_token_time = time()
        return _token

    @staticmethod
    def __logs_and_raise(msg: str):
        logger.error(msg)
        raise Exception(msg)
