"""Tests for the endpoints module."""

from pathlib import Path

import pytest

from rdf_uploader.endpoints import EndpointClient, EndpointType, RDFoxEndpoint


def test_endpoint_client_init():
    """Test initializing the endpoint client."""
    client = EndpointClient(
        endpoint_url="http://example.org/sparql",
        endpoint_type=EndpointType.BLAZEGRAPH,
        timeout=30,
    )
    assert client.endpoint_url == "http://example.org/sparql"
    assert client.endpoint_type == EndpointType.BLAZEGRAPH
    assert client.timeout == 30
    assert client.username is not None
    assert client.password is not None
    assert client.content_type is None


def test_endpoint_client_init_with_auth_and_content_type(test_username, test_password):
    """Test initializing the endpoint client with authentication and content type."""
    client = EndpointClient(
        endpoint_url="http://example.org/sparql",
        endpoint_type=EndpointType.MARKLOGIC,
        timeout=30,
        username=test_username,
        password=test_password,
        content_type="application/rdf+xml",
    )
    assert client.endpoint_url == "http://example.org/sparql"
    assert client.endpoint_type == EndpointType.MARKLOGIC
    assert client.timeout == 30
    assert client.username == test_username
    assert client.password == test_password
    assert client.content_type == "application/rdf+xml"


def test_endpoint_client_init_with_store_name():
    """Test initializing the endpoint client with a custom store name."""
    custom_store = "custom-store"
    client = EndpointClient(
        endpoint_url="http://example.org/sparql",
        endpoint_type=EndpointType.RDFOX,
        store_name=custom_store,
    )
    assert client.store_name == custom_store

    # Verify the store name is passed to the RDFox endpoint strategy
    assert isinstance(client.endpoint_strategy, RDFoxEndpoint)
    assert client.endpoint_strategy.store_name == custom_store


@pytest.mark.parametrize(
    "endpoint_type",
    [
        EndpointType.BLAZEGRAPH,
        EndpointType.MARKLOGIC,
        EndpointType.NEPTUNE,
        EndpointType.RDFOX,
        EndpointType.STARDOG,
    ],
)
def test_endpoint_type_initialization(endpoint_type):
    """Test that the client is initialized correctly for different endpoint types."""
    client = EndpointClient(
        endpoint_url="http://example.org/sparql",
        endpoint_type=endpoint_type,
    )

    # Check that the client is initialized with the correct endpoint type
    assert client.endpoint_type == endpoint_type

    # Check that the strategy is of the correct type
    strategy_class_name = client.endpoint_strategy.__class__.__name__
    assert strategy_class_name.lower().startswith(endpoint_type.value.lower())


@pytest.mark.asyncio()
async def test_upload_data_blazegraph(
    sample_turtle_file, blazegraph_endpoint, blazegraph_enabled
):
    """Test uploading data to a BlazeGraph endpoint."""
    if not blazegraph_enabled:
        pytest.skip("BlazeGraph tests are disabled")
    # Test the upload_data method
    client = EndpointClient(
        endpoint_url=blazegraph_endpoint,
        endpoint_type=EndpointType.BLAZEGRAPH,
    )

    # Read the file content using Path
    content = Path(sample_turtle_file).read_text(encoding="utf-8")

    # Upload to a test graph
    test_graph = "http://example.org/test-graph"
    success, status_code = await client.upload_data(
        data=content,
        graph=test_graph,
        content_type="text/turtle",
    )

    assert success is True
    assert isinstance(status_code, int)
    assert 200 <= status_code < 300  # Success status codes


@pytest.mark.asyncio()
async def test_upload_data_rdfox(
    sample_turtle_file,
    rdfox_endpoint,
    rdfox_username,
    rdfox_password,
    rdfox_enabled,
    rdfox_store_name,
):
    """Test uploading data to an RDFox endpoint."""
    if not rdfox_enabled:
        pytest.skip("RDFox tests are disabled")
    # Test the upload_data method
    client = EndpointClient(
        endpoint_url=rdfox_endpoint,
        endpoint_type=EndpointType.RDFOX,
        username=rdfox_username,
        password=rdfox_password,
        store_name=rdfox_store_name,
    )

    # Read the file content using Path
    content = Path(sample_turtle_file).read_text(encoding="utf-8")

    # Upload to a test graph
    test_graph = "http://example.org/test-graph"
    success, status_code = await client.upload_data(
        data=content,
        graph=test_graph,
        content_type="text/turtle",
    )

    assert success is True
    assert isinstance(status_code, int)
    assert 200 <= status_code < 300  # Success status codes


@pytest.mark.asyncio()
async def test_upload_data_stardog(
    sample_turtle_file,
    stardog_endpoint,
    stardog_username,
    stardog_password,
    stardog_enabled,
):
    """Test uploading data to a StarDog endpoint."""
    if not stardog_enabled:
        pytest.skip("StarDog tests are disabled")
    # Test the upload_data method
    client = EndpointClient(
        endpoint_url=stardog_endpoint,
        endpoint_type=EndpointType.STARDOG,
        username=stardog_username,
        password=stardog_password,
    )

    # Read the file content using Path
    content = Path(sample_turtle_file).read_text(encoding="utf-8")

    # Upload to a test graph
    test_graph = "http://example.org/test-graph"
    success, status_code = await client.upload_data(
        data=content,
        graph=test_graph,
        content_type="text/turtle",
    )

    assert success is True
    assert isinstance(status_code, int)
    assert 200 <= status_code < 300  # Success status codes
