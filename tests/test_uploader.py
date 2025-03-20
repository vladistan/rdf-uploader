"""Tests for the uploader module."""

from pathlib import Path
from typing import Any

import httpx
import pytest

from rdf_uploader.endpoints import EndpointType
from rdf_uploader.file_readers import detect_content_type, get_reader
from rdf_uploader.uploader import upload_rdf_file, upload_rdf_files


def test_detect_content_type():
    """Test content type detection based on file extension."""
    assert detect_content_type(Path("test.ttl")) == "text/turtle"
    assert detect_content_type(Path("test.turtle")) == "text/turtle"
    assert detect_content_type(Path("test.nt")) == "application/n-triples"
    assert detect_content_type(Path("test.n3")) == "text/n3"
    assert detect_content_type(Path("test.nq")) == "application/n-quads"
    assert detect_content_type(Path("test.nquads")) == "application/n-quads"
    assert detect_content_type(Path("test.rdf")) == "application/rdf+xml"
    assert detect_content_type(Path("test.xml")) == "application/rdf+xml"
    assert detect_content_type(Path("test.jsonld")) == "application/ld+json"
    assert detect_content_type(Path("test.json")) == "application/rdf+json"
    assert detect_content_type(Path("test.trig")) == "application/trig"
    # Default to Turtle if unknown
    assert detect_content_type(Path("test.unknown")) == "text/turtle"


class StatsCollector:
    """Helper class for collecting stats in tests."""

    def __init__(self):
        self.history: list[dict[str, Any]] = []

    def callback(self, stats: dict[str, Any]) -> None:
        """Callback function for collecting stats."""
        self.history.append(stats)

    def assert_stats_collected(self) -> None:
        """Assert that stats were collected correctly."""
        assert len(self.history) > 0
        assert "total_triples" in self.history[0]
        assert "uploaded_triples" in self.history[0]
        assert "triples_per_second" in self.history[0]
        assert "batch_num" in self.history[0]
        assert "batch_count" in self.history[0]
        assert "status_code" in self.history[0]


async def run_endpoint_test(
    sample_file: Path,
    endpoint_url: str,
    endpoint_type: EndpointType,
    enabled: bool = True,
    content_type: str = "application/n-quads",
    batch_size: int = 100,
    username: str | None = None,
    password: str | None = None,
    expected_status: int | None = None,
    skip_message: str | None = None,
    store_name: str | None = None,
) -> None:
    # Skip test if endpoint is not enabled
    if not enabled:
        pytest.skip(
            skip_message or f"{endpoint_type.value.capitalize()} tests are disabled"
        )

    # Create a stats collector
    stats = StatsCollector()

    # Run the upload
    result = await upload_rdf_file(
        file_path=sample_file,
        endpoint=endpoint_url,
        endpoint_type=endpoint_type,
        username=username,
        password=password,
        content_type=content_type,
        batch_size=batch_size,
        stats_callback=stats.callback,
        store_name=store_name,
    )

    # Check results
    assert isinstance(result, bool)
    stats.assert_stats_collected()

    # Check status code if expected
    if expected_status and len(stats.history) > 0:
        assert stats.history[0]["status_code"] == expected_status
    # Otherwise just check that it's a success code (2xx)
    elif len(stats.history) > 0:
        assert (
            200 <= stats.history[0]["status_code"] < 300
        ), f"Expected success status code, got {stats.history[0]['status_code']}"


@pytest.mark.asyncio()
async def test_upload_rdf_file(
    sample_nq_file,
    marklogic_endpoint,
    marklogic_username,
    marklogic_password,
    marklogic_enabled,
):
    """Test uploading a single RDF file."""
    await run_endpoint_test(
        sample_file=sample_nq_file,
        endpoint_url=marklogic_endpoint,
        endpoint_type=EndpointType.MARKLOGIC,
        enabled=marklogic_enabled,
        username=marklogic_username,
        password=marklogic_password,
        content_type="application/n-quads",  # MarkLogic accepts this content type
        skip_message="MarkLogic tests are disabled",
    )


@pytest.mark.asyncio()
async def test_upload_rdf_file_with_streaming(
    sample_nq_file,
    marklogic_endpoint,
    marklogic_username,
    marklogic_password,
    marklogic_enabled,
):
    """Test uploading a single RDF file with streaming."""
    await run_endpoint_test(
        sample_file=sample_nq_file,
        endpoint_url=marklogic_endpoint,
        endpoint_type=EndpointType.MARKLOGIC,
        enabled=marklogic_enabled,
        username=marklogic_username,
        password=marklogic_password,
        content_type="application/n-quads",
        batch_size=5,  # Small batch size to test streaming
        skip_message="MarkLogic tests are disabled",
    )

    # Verify batches are created correctly
    reader = get_reader(sample_nq_file)
    batches = await reader.read_batches(batch_size=5)
    assert len(batches) > 0


@pytest.mark.asyncio()
async def test_upload_rdf_files_with_error(
    sample_nq_file,
    marklogic_endpoint,
    marklogic_username,
    marklogic_password,
    marklogic_enabled,
    monkeypatch,
):
    """Test that upload_rdf_files correctly captures and returns error details."""
    # Skip test if MarkLogic is not enabled
    if not marklogic_enabled:
        pytest.skip("MarkLogic tests are disabled")

    # Mock upload_rdf_file to raise an exception
    def mock_upload_with_error(*args, **kwargs):  # noqa: ARG001
        raise httpx.HTTPStatusError(  # noqa: TRY003
            "Error uploading data: 400 Bad Request",
            request=httpx.Request("POST", "http://example.com"),
            response=httpx.Response(
                400, request=httpx.Request("POST", "http://example.com")
            ),
        )

    monkeypatch.setattr("rdf_uploader.uploader.upload_rdf_file", mock_upload_with_error)

    # Run the upload_rdf_files function
    results = await upload_rdf_files(
        files=[sample_nq_file],
        endpoint=marklogic_endpoint,
        endpoint_type=EndpointType.MARKLOGIC,
        username=marklogic_username,
        password=marklogic_password,
    )

    # Check that the results contain error details
    assert sample_nq_file in results
    assert isinstance(results[sample_nq_file], dict)
    assert results[sample_nq_file]["success"] is False
    assert "error_type" in results[sample_nq_file]
    assert "error_message" in results[sample_nq_file]
    assert results[sample_nq_file]["error_type"] == "HTTPStatusError"
    assert "400 Bad Request" in results[sample_nq_file]["error_message"]


@pytest.mark.asyncio()
async def test_upload_rdf_file_to_neptune(
    sample_nq_file, neptune_endpoint, neptune_enabled
):
    """Test uploading a single RDF file to Neptune."""
    await run_endpoint_test(
        sample_file=sample_nq_file,
        endpoint_url=neptune_endpoint,
        endpoint_type=EndpointType.NEPTUNE,
        enabled=neptune_enabled,
        content_type="text/nquads",
        expected_status=200,
        skip_message="Neptune tests are disabled",
    )


@pytest.mark.asyncio()
async def test_upload_rdf_file_to_blazegraph(
    sample_nq_file, blazegraph_endpoint, blazegraph_enabled
):
    """Test uploading a single RDF file to Blazegraph."""
    await run_endpoint_test(
        sample_file=sample_nq_file,
        endpoint_url=blazegraph_endpoint,
        endpoint_type=EndpointType.BLAZEGRAPH,
        enabled=blazegraph_enabled,
        content_type="text/nquads",
        expected_status=200,
        skip_message="BlazeGraph tests are disabled",
    )


@pytest.mark.asyncio()
async def test_upload_rdf_file_to_rdfox(
    sample_nq_file,
    rdfox_endpoint,
    rdfox_username,
    rdfox_password,
    rdfox_store_name,
    rdfox_enabled,
):
    """Test uploading a single RDF file to RDFox."""
    await run_endpoint_test(
        sample_file=sample_nq_file,
        endpoint_url=rdfox_endpoint,
        endpoint_type=EndpointType.RDFOX,
        enabled=rdfox_enabled,
        username=rdfox_username,
        password=rdfox_password,
        content_type="application/n-quads",
        store_name=rdfox_store_name,
        skip_message="RDFox tests are disabled",
    )


@pytest.mark.asyncio()
async def test_upload_rdf_file_to_stardog(
    sample_nq_file,
    stardog_endpoint,
    stardog_username,
    stardog_password,
    stardog_enabled,
):
    """Test uploading a single RDF file to Stardog."""
    await run_endpoint_test(
        sample_file=sample_nq_file,
        endpoint_url=stardog_endpoint,
        endpoint_type=EndpointType.STARDOG,
        enabled=stardog_enabled,
        username=stardog_username,
        password=stardog_password,
        content_type="application/n-quads",
        skip_message="StarDog tests are disabled",
    )
