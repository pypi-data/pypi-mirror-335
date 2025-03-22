"""
Transport module for Opentmi python client
"""
import json
import logging

from requests import Response, RequestException

from opentmi_client.transport.HttpAdapter import create_http_session

from urllib.parse import urlencode, quote
from opentmi_client.utils import resolve_host, resolve_token, TransportException

NOT_FOUND = 404

logger = logging.getLogger(__name__)


class Transport(object):
    """
    Transport class which handle communication layer
    Mostly wrappers http rest requests to more simple APIs
    """

    __request_timeout = 10

    def __init__(self, host="127.0.0.1", port=None, token=None):
        """
        Constructor for Transport
        :param host: Hostname as a String
        :param port: optional port as a positive Integer
        :param token: optional token
        """
        self.__token = None
        self.__host = None
        self._session = None
        if token:
            self.set_token(token)

        self.set_host(host, port)
        logger.info("OpenTMI host: %s", self.host)

    def set_host(self, host, port=None):
        """
        Set host address and port
        :param host:
        :param port:
        :return: None
        """
        self.__host = resolve_host(host, port)
        token = resolve_token(host)
        self._session = create_http_session(self.__host)
        if token:
            self.__host = self.__host.replace(token + "@", "")
            self.set_token(token)

    @property
    def host(self):
        """
        Getter for host
        :return: host as a string
        """
        return self.__host

    @property
    def token(self):
        """
        Getter for token
        :return: token as a string or None
        """
        return self.__token

    def set_token(self, token):
        """
        Set authentication token
        :param token:
        :return: Transport
        """
        self.__token = token
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        return self

    def has_token(self):
        """
        Check if token is available
        :return: Boolean True if token exists, otherwise False
        """
        return self.__token is not None

    def get_url(self, path):
        """
        Create url from path
        :param path: string, e.g. "/auth/login"
        :return: url as a string
        """
        return self._session.base_url_join(path)

    @staticmethod
    def _params_encode(params):
        """
        Encode parameters
        :param params: Dict of url parameters
        """
        if not params:
            return params
        params = {k: quote(v) for k, v in params.items()}
        return params

    def get_json(self, url, params=None):
        """
        GET request
        :param url: url as a string
        :param params: url parameters as dict
        :raise TransportException: when something goes wrong
        :return: dict object or None if not found
        """
        try:
            logger.debug("GET: %s?%s", url, urlencode(params) if params else '')
            response = self._session.get(url, params=Transport._params_encode(params))
            if Transport.is_success(response):
                return response.json()
            if response.status_code == NOT_FOUND:
                logger.warning("not found")
            else:
                logger.warning("Request failed: %s (code: %s)",
                                    response.text, str(response.status_code))
                raise TransportException(response.text, response.status_code)
        except RequestException as error:
            logger.warning("Connection error %s", error)
            raise TransportException(str(error))
        except (ValueError, TypeError) as error:
            raise TransportException(str(error))
        return None

    def post_json(self, url, payload, files=None):
        """
        POST request
        :param url:
        :param payload:
        :param files:
        :return: response as dict
        """
        try:
            response = self._session.post(url, json=payload, files=files if not None else [])
            if Transport.is_success(response):
                return response.json()
            logger.warning("status_code: %s", str(response.status_code))
            logger.warning(response.text)
            raise TransportException(response.text, response.status_code)
        except RequestException as error:
            logger.warning(error)
            raise TransportException(str(error))
        except (ValueError, TypeError, KeyError) as error:
            raise TransportException(error)

    def put_json(self, url, payload):
        """
        PUT requests
        :param url:
        :param payload: dict
        :return: response as a dict
        """
        try:
            response = self._session.put(url, json=payload)
            if Transport.is_success(response):
                data = json.loads(response.text)
                return data
            logger.warning("status_code: %s", str(response.status_code))
            logger.warning(response.text)
            raise TransportException(response.text, response.status_code)
        except RequestException as error:
            logger.warning(error)
            raise TransportException(str(error))
        except (ValueError, TypeError) as error:
            raise TransportException(error)
        except Exception as error:
            logger.warning(error)
            raise TransportException(str(error))

    @staticmethod
    def is_success(response):
        """
        Check if status_code is success range
        :param response:
        :return:
        """
        assert isinstance(response, Response)
        code = response.status_code
        return 300 > code >= 200
