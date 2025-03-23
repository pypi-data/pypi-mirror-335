import logging
from typing import Optional
from urllib.parse import urljoin

import requests

# from requests_toolbelt.adapters.socket_options import TCPKeepAliveAdapter
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_random_exponential

log = logging.getLogger(__name__)


def is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, requests.exceptions.HTTPError):
        return exception.response.status_code in (429,)
    return False


DEFAULT_RETRYING = Retrying(
    retry=retry_if_exception(is_retryable),
    wait=wait_random_exponential(multiplier=1, max=30),
    stop=stop_after_attempt(5),
    after=lambda state: log.error("failed attempt: %s", state.outcome.exception()),
    reraise=True,
)


class SimpleHttpClient:
    """Simple http client with retry and keep-alive support."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        session: requests.Session = None,
        # keep_alive_idle: int = 120,
        # keep_alive_count: int = 20,
        # keep_alive_interval: int = 30,
        extra_session_settings: dict = None,
        retrying: Retrying = DEFAULT_RETRYING,
    ):
        self.base_url = base_url
        self.session = session or requests.Session()
        # https://requests.readthedocs.io/en/latest/user/advanced/#keep-alive
        # self.session.mount(
        #     base_url,
        #     TCPKeepAliveAdapter(
        #         idle=keep_alive_idle,
        #         count=keep_alive_count,
        #         interval=keep_alive_interval,
        #     ),
        # )
        if extra_session_settings:
            for k, v in extra_session_settings.items():
                setattr(self.session, k, v)

        self.retrying = retrying

    def _request(self, method: str, url: str, **kwargs):
        log.debug("http request: %s %s", method, url)
        res = self.session.request(method, url, **kwargs)
        if res.status_code >= 400:
            log.error("response status: %s", res.status_code)
            log.error("response text: %s", res.text)
            log.error("response headers: %s", res.headers)
        res.raise_for_status()
        return res

    def request(self, method: str, path: str, **kwargs):
        url = urljoin(self.base_url, path)
        res = self.retrying(self._request, method, url, **kwargs)
        return res

    def get(self, path: str, **kwargs):
        return self.request("get", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("post", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.request("delete", path, **kwargs)
