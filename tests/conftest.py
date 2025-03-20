import os
import re
from pathlib import Path

import pytest


def get_credential(key: str, default: str = "") -> str:
    value = os.environ.get(key)
    if value is not None:
        return value

    envrc_path = Path(__file__).parent.parent / ".envrc"
    if envrc_path.exists():
        content = envrc_path.read_text()
        pattern = rf'export\s+{key}=(["\']?)(.+?)(\1)(?:\s|$)'
        match = re.search(pattern, content)
        if match:
            return match.group(2)

    return default


TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture()
def sample_turtle_file() -> Path:
    return TEST_DATA_DIR / "sample.ttl"


@pytest.fixture()
def sample_nq_file() -> Path:
    return TEST_DATA_DIR / "sample.nq"


@pytest.fixture()
def single_line_nq_file() -> Path:
    return TEST_DATA_DIR / "single-triple.nt"


@pytest.fixture()
def marklogic_enabled() -> bool:
    return get_credential("MARKLOGIC_ENABLED", "true").lower() == "true"


@pytest.fixture()
def marklogic_endpoint() -> str:
    return get_credential("MARKLOGIC_ENDPOINT")


@pytest.fixture()
def neptune_enabled() -> bool:
    return get_credential("NEPTUNE_ENABLED", "true").lower() == "true"


@pytest.fixture()
def neptune_endpoint() -> str:
    return get_credential("NEPTUNE_ENDPOINT")


@pytest.fixture()
def blazegraph_enabled() -> bool:
    return get_credential("BLAZEGRAPH_ENABLED", "true").lower() == "true"


@pytest.fixture()
def blazegraph_endpoint() -> str:
    return get_credential("BLAZEGRAPH_ENDPOINT")


@pytest.fixture()
def rdfox_enabled() -> bool:
    return get_credential("RDFOX_ENABLED", "true").lower() == "true"


@pytest.fixture()
def rdfox_endpoint() -> str:
    return get_credential("RDFOX_ENDPOINT")


@pytest.fixture()
def stardog_enabled() -> bool:
    return get_credential("STARDOG_ENABLED", "true").lower() == "true"


@pytest.fixture()
def stardog_endpoint() -> str:
    return get_credential("STARDOG_ENDPOINT")


@pytest.fixture()
def test_username() -> str:
    return get_credential("TEST_USERNAME")


@pytest.fixture()
def test_password() -> str:
    return get_credential("TEST_PASSWORD")


@pytest.fixture()
def marklogic_username() -> str:
    return get_credential("MARKLOGIC_USERNAME")


@pytest.fixture()
def marklogic_password() -> str:
    return get_credential("MARKLOGIC_PASSWORD")


@pytest.fixture()
def rdfox_username() -> str:
    return get_credential("RDFOX_USERNAME")


@pytest.fixture()
def rdfox_password() -> str:
    return get_credential("RDFOX_PASSWORD")


@pytest.fixture()
def rdfox_store_name() -> str:
    return get_credential("RDFOX_STORE_NAME")


@pytest.fixture()
def stardog_username() -> str:
    return get_credential("STARDOG_USERNAME")


@pytest.fixture()
def stardog_password() -> str:
    return get_credential("STARDOG_PASSWORD")
