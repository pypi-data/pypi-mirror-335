import logging
import re
import time
from urllib.parse import urljoin

import requests
from google.auth.transport.requests import AuthorizedSession

from dbox.utils.http_client import SimpleHttpClient

log = logging.getLogger(__name__)


class AirflowRestClient(SimpleHttpClient):
    def __init__(
        self,
        session: requests.Session,
        base_url: str = "http://localhost:8080/api/v1/",
        fetch_limit=100,
    ) -> None:
        self.base_url = base_url
        self.session = session
        self.fetch_limit = fetch_limit
        super().__init__(base_url=base_url, session=session)

    def login(self, username, password):
        """Perform the login with user, password using airflow.api.auth.backend.session"""
        login_url = urljoin(self.base_url, "/login")
        res = self.session.get(login_url)
        res.raise_for_status()

        # extract csrf token
        csrf_token = re.search(r"""csrfToken.*["'](.*)["']""", res.text).group(1)
        res = self.session.post(
            login_url,
            data={"username": username, "password": password, "csrf_token": csrf_token},
        )
        res.raise_for_status()

    def list_dags(self, **kwargs):
        def dags_paginator(limit, offset):
            res = self.request("GET", "dags", params={"limit": limit, "offset": offset, **kwargs}).json()
            return res["total_entries"], res["dags"]

        return _iterate_over_paginator(dags_paginator, self.fetch_limit)

    def list_variables(self):
        def variables_paginator(limit, offset):
            res = self.request("GET", "variables", params={"limit": limit, "offset": offset}).json()
            return res["total_entries"], res["variables"]

        return _iterate_over_paginator(variables_paginator, self.fetch_limit)

    def list_connections(self):
        def connections_paginator(limit, offset):
            res = self.request("GET", "connections", params={"limit": limit, "offset": offset}).json()
            return res["total_entries"], res["connections"]

        return _iterate_over_paginator(connections_paginator, self.fetch_limit)

    def get_variable(self, key, not_found_ok=False):
        res = self.request("GET", "variables/" + key, check_response=False)
        if res.status_code == 404 and not_found_ok:
            return None
        res.raise_for_status()
        return res.json()

    def create_variable(self, key, value):
        return self.request("POST", "variables", json={"key": key, "value": value}).json()

    def patch_variable(self, key, value: str):
        return self.request(
            "PATCH",
            "variables/" + key,
            json={"key": key, "value": value},
            params={"update_mask": "value"},
        )

    def delete_variable(self, key):
        return self.request("DELETE", "variables/" + key)

    def list_dag_runs(self, dag_id, **kwargs):
        def dag_runs_paginator(limit, offset, **kwargs):
            res = self.request(
                "GET",
                f"dags/{dag_id}/dagRuns",
                params={"limit": limit, "offset": offset, **kwargs},
            ).json()
            return res["total_entries"], res["dag_runs"]

        return _iterate_over_paginator(dag_runs_paginator, self.fetch_limit, **kwargs)

    def trigger_dag_run(self, dag_id, conf=None, wait: bool = True, fetch_interval_secs=10):
        body = {"conf": conf} if conf else {}
        res = self.request("post", f"dags/{dag_id}/dagRuns", json=body)
        dag_run = res.json()
        log.info("Triggered dag run: %s", dag_run)
        dag_run_id = dag_run["dag_run_id"]
        while wait:
            state = dag_run["state"]
            if state in ("success", "failed"):
                log.info("Dag run completed with state %s", state)
                break
            elif state in ("queued", "running"):
                log.info("Dag run is at state %s", state)
                time.sleep(fetch_interval_secs)
                dag_run = self.request("get", f"dags/{dag_id}/dagRuns/{dag_run_id}").json()
        return dag_run


def _iterate_over_paginator(paginator_fn, limit, *args, **kwargs):
    "Support iterating over paginated resources"
    offset = 0
    total = None
    while True:
        _total, items = paginator_fn(*args, limit=limit, offset=offset, **kwargs)
        if total is not None and _total != total:
            raise RuntimeError("some items may have been created or removed in the mean time")
        if total is None:
            total = _total
        offset = offset + limit
        yield from items
        if offset >= total:
            break


class GcpComposerRestClient(AirflowRestClient):
    def __init__(self, *, project, region, environment_name, credentials, fetch_limit=100) -> None:
        authed_session = AuthorizedSession(credentials=credentials)
        log.debug("getting environment details")
        url = "https://composer.googleapis.com/v1/projects/{}/locations/{}/environments/{}".format(
            project, region, environment_name
        )
        res = authed_session.request("GET", url)
        res.raise_for_status()
        environment = res.json()
        self.composer_environment = environment
        base_url = environment["config"]["airflowUri"] + "/api/v1/"
        super().__init__(session=authed_session, fetch_limit=fetch_limit, base_url=base_url)

    @property
    def bucket(self):
        # composer_environment["storageConfig"]["bucket"]
        return self.composer_environment["config"]["dagGcsPrefix"]
