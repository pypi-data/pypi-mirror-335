"""
HTTPAdapter
"""
import logging
import urllib.parse
from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 30  # seconds

logger = logging.getLogger(__name__)


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    Timeout adapter that pass default timeout
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor for TimeoutHTTPAdapter
        :param args: HttpAdapter args
        :param kwargs: HTTPAdapter kwargs
        """
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):  # pylint: disable=arguments-differ
        """ HTTPAdapter send method """
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class LogRetry(Retry):
    """
    Adding extra logs before making a retry request
    """

    def __init__(self, *args, **kwargs):
        logger.debug(f'Retry (total: {kwargs.get("total")})')
        super().__init__(*args, **kwargs)


def create_http_session(base_url: str) -> requests.Session:
    """
    Create requests session
    @example
    > s = create_http_session('http://localhost', 'mytoken')
    > s.get(s.base_url_join('/api'))
    :param base_url: base url
    :return: Session instance
    """
    retry_strategy = LogRetry(
        redirect=2,
        total=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    retry_adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount(base_url, retry_adapter)
    session.headers.update({"content-type": "application/json",
                            "Connection": "keep-alive"})
    session.base_url_join = lambda path: urllib.parse.urljoin(base_url, path)
    return session
