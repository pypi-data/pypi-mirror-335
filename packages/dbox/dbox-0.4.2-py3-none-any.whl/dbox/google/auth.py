import asyncio
import json
import logging
from pathlib import Path
from random import randint
from threading import Thread
from typing import Tuple

import google.auth
from google.auth.credentials import Credentials
from google.oauth2.credentials import Credentials as Oauth2Credentials
from google_auth_oauthlib.flow import Flow

log = logging.getLogger(__name__)


class ServerContextManager:
    def __init__(self, port: int):
        self.port = port
        self.code = None
        self.server = None
        self.thread = None

    def __enter__(self):
        import uvicorn
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import Response
        from starlette.routing import Route

        def callback(request: Request):
            qs = request.query_params
            codes = qs.get("code")
            if codes:
                self.code = codes
                log.debug("got code response - shutting down server")
                if self.server:
                    self.server.should_exit = True
            scope = request.scope
            body = {
                "type": scope["type"],
                "asgi": scope["asgi"],
                "method": scope["method"],
                "scheme": scope["scheme"],
                "path": scope["path"],
                "query_string": scope["query_string"],
                "headers": scope["headers"],
            }

            def encode(v):
                if isinstance(v, bytes):
                    return v.decode("utf-8")
                return str(v)

            return Response(
                content=json.dumps(body, default=encode),
                status_code=200,
                media_type="application/json",
            )

        app = Starlette(routes=[Route("/", callback)])

        config = uvicorn.Config(app, host="localhost", port=self.port, log_level="error")
        self.server = uvicorn.Server(config)
        log.debug("starting server at port %s", self.port)

        self.thread = Thread(target=self.server.run)
        self.thread.start()

        return self

    def wait_for_code(self):
        self.thread.join()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            self.server.should_exit = True
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.server.shutdown())
            else:
                loop.run_until_complete(self.server.shutdown())
        if self.thread:
            self.thread.join()
        log.debug("server shutdown")
        return False


def google_login(scopes, secret_path, port=None):
    port = port or randint(10001, 10999)
    flow = Flow.from_client_secrets_file(
        secret_path,
        scopes=scopes,
        redirect_uri=f"http://localhost:{port}",
        autogenerate_code_verifier=True,
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    log.info("Authorization URL (copied): {}".format(auth_url))
    try:
        from pyperclip import copy

        copy(auth_url)
    except Exception as e:
        log.warning("failed to copy to clipboard: %s", e)
    with ServerContextManager(port) as server:
        server.wait_for_code()

        flow.fetch_token(code=server.code)
        return flow.credentials


def read_user_credentials(path):
    path = Path(path).expanduser()
    with open(path) as f:
        creds = Oauth2Credentials.from_authorized_user_info(json.load(f))
        return creds


def default_credentials(
    scopes=None,
) -> Tuple[Credentials, str]:
    if scopes is None:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    creds, project = google.auth.default(scopes)
    return creds, project


def get_user_email(creds):
    import google.auth.transport.requests
    import google.oauth2.id_token
    from google.auth.transport.requests import AuthorizedSession

    auth_req = google.auth.transport.requests.Request(AuthorizedSession(credentials=creds))
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, "https://hello.com")

    return id_token


def get_user_email_of_credentials(creds: Credentials):
    import google.auth.transport.requests
    import google.oauth2.id_token
    from google.auth.transport.requests import AuthorizedSession

    auth_req = google.auth.transport.requests.Request(AuthorizedSession(credentials=creds))
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, "https://hello.com")

    return id_token["email"]
