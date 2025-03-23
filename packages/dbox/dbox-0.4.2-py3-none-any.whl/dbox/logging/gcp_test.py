import logging
import os

import pytest

from dbox.ctx import set_context

from .context import set_log_labels
from .gcp import CloudLoggingHandler

log = logging.getLogger(__name__)


def test_send_log_to_gcp():
    if "TEST_GCP_LOGGING" not in os.environ:
        raise pytest.skip("TEST_GCP_LOGGING is not set")
    from google.cloud.logging_v2 import Client

    client = Client(project="vix-one")
    resource = {"type": "generic_task", "labels": {"job": "test", "namespace": "dbox"}}
    handler = CloudLoggingHandler(client=client, resource=resource)
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
    log.info("This is a test log message")
    try:
        1 / 0  # noqa
    except Exception as e:
        log.exception("This is an exception", exc_info=e)
    with set_log_labels(scope="test"):
        log.warning("This is a warning message")

    with set_context(http_request={"requestMethod": "GET", "requestUrl": "http://example.com"}):
        log.info("This is an error message")
