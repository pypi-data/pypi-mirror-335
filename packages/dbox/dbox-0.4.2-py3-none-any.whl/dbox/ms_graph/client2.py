import logging
import os
import sys
from http.server import HTTPServer

import msal
import requests

log = logging.getLogger(__name__)


class MsGraphClient:
    def __init__(
        self,
        application_id: str,
        oauth_authority: str = "https://login.microsoftonline.com/organizations",
        base_url="https://graph.microsoft.com/v1.0",
    ):
        self.base_url = base_url
        self.application_id = application_id
        self.access_token = None
        self.oauth_authority = oauth_authority
        self.app = msal.PublicClientApplication(
            client_id=self.application_id,
            authority=self.oauth_authority,
            exclude_scopes=["offline_access"],  # no need refresh token
        )
        self.sess = requests.Session()

    def authorize(self, scopes, *, port=9090):
        if "INSIDE_DOCKER" in os.environ:
            log.info("authorizing inside docker container")
            self._authorize_in_docker(scopes, port)
        else:
            self._authorize(scopes, port)

    def request(self, method: str, url: str, *args, **kwargs):
        headers = kwargs.pop("headers", {})
        if not url.startswith("https://"):
            url = self.base_url + url
        log.info("requesting %s", url)
        assert self.access_token, "must call authorize first"
        headers["authorization"] = "bearer " + self.access_token
        res = self.sess.request(method, url, *args, headers=headers, **kwargs)
        res.raise_for_status()
        return res

    def quick_get(self, url: str):
        res = self.request("get", url)
        return res.json()["value"]

    def _authorize(self, scopes, port):
        res = self.app.acquire_token_interactive(scopes=scopes, port=port, prompt="select_account", timeout=60)
        if "error" in res:
            raise RuntimeError("fetching access token failed with response %s", res)
        log.debug("auth response %s", res)
        self.access_token = res["access_token"]

    def _authorize_in_docker(self, scopes, port):
        from msal.oauth2cli.authcode import is_wsl

        class OpenAuthCodeHttpServer(HTTPServer):
            """A auth code http server that listens on 0.0.0.0"""

            def __init__(self, server_address, *args, **kwargs):
                _, port = server_address
                if port and (sys.platform == "win32" or is_wsl()):
                    # The default allow_reuse_address is True. It works fine on non-Windows.
                    # On Windows, it undesirably allows multiple servers listening on same port,
                    # yet the second server would not receive any incoming request.
                    # So, we need to turn it off.
                    self.allow_reuse_address = False
                super(OpenAuthCodeHttpServer, self).__init__(("0.0.0.0", port), *args, **kwargs)

            def handle_timeout(self):
                raise RuntimeError("Timeout. No auth response arrived.")  # Terminates this server

        from unittest.mock import patch

        # patch _AuthCodeHttpServer so that it listens on 0.0.0.0
        # otherwise the hardcoded 127.0.0.1 will not allow us to do authentication inside docker
        with patch(
            target="msal.oauth2cli.authcode._AuthCodeHttpServer",
            new=OpenAuthCodeHttpServer,
        ):
            return self._authorize(scopes, port)
