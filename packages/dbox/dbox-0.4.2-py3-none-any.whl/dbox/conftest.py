import logging
import sys
from pathlib import Path

import pytest
from google.cloud import bigquery

log = logging.getLogger(__name__)

root = Path(__file__).parent
for path in [
    Path("~/space").expanduser(),
]:
    if path.as_posix() not in sys.path:
        sys.path.append(path.as_posix())


@pytest.fixture(autouse=True)
def run_around_tests():
    # Code that will run before each test
    # Print a linebreak for better readability
    print("\n", end="")  # noqa: T201
    yield
    # Code that will run after each test


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    from dbox.logging.colored import setup_colored_logging

    setup_colored_logging()
    logging.getLogger("luna").setLevel("DEBUG")
    # logging.getLogger("psycopg").setLevel("DEBUG")


@pytest.fixture(scope="session", autouse=True)
def root_dir():
    return root


@pytest.fixture(scope="session")
def bqclient():
    return bigquery.Client(project="vix-one")


@pytest.fixture(scope="session")
def gads_developer_token():
    from dbox.env import GOOGLE_ADS_DEVELOPER_TOKEN

    return GOOGLE_ADS_DEVELOPER_TOKEN


@pytest.fixture(scope="session")
def google_credentials():
    from dbox.google.auth import read_user_credentials

    return read_user_credentials("leuduan@gmail.com.json")
