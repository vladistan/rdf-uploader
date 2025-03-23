import asyncio
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rdf_uploader.endpoints import EndpointClient, EndpointType
from rdf_uploader.file_readers import detect_content_type, get_reader


class StatsCollector:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.total_triples = 0
        self.uploaded_triples = 0
        self.start_time = time.time()
        self.batch_num = 0
        self.callback: Callable[[dict[str, Any]], None] | None = None

    def set_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self.callback = callback

    def set_total_triples(self, total: int) -> None:
        self.total_triples = total

    def update(self, batch_count: int, status_code: int) -> None:
        self.batch_num += 1
        self.uploaded_triples += batch_count

        if not self.callback:
            return

        elapsed_time = time.time() - self.start_time
        triples_per_second = (
            self.uploaded_triples / elapsed_time if elapsed_time > 0 else 0
        )

        self.callback(
            {
                "file": str(self.file_path),
                "total_triples": self.total_triples,
                "uploaded_triples": self.uploaded_triples,
                "progress_percent": (self.uploaded_triples / self.total_triples) * 100
                if self.total_triples > 0
                else 0,
                "elapsed_time": elapsed_time,
                "triples_per_second": triples_per_second,
                "batch_num": self.batch_num,
                "batch_count": batch_count,
                "status_code": status_code,
            }
        )


async def upload_rdf_file(
    file_path: Path,
    endpoint: str | None = None,
    endpoint_type: EndpointType = EndpointType.GENERIC,
    graph: str | None = None,
    username: str | None = None,
    password: str | None = None,
    content_type: str | None = None,
    batch_size: int = 100,
    stats_callback: Callable[[dict[str, Any]], None] | None = None,
    store_name: str | None = None,
) -> bool:
    """
    Upload a single RDF file to a SPARQL endpoint.

    Args:
        file_path: Path to the RDF file to upload
        endpoint: SPARQL endpoint URL (optional, can be read from environment variables)
        endpoint_type: Type of SPARQL endpoint
        graph: Named graph to upload to
        username: Username for authentication (optional, can be read from environment variables)
        password: Password for authentication (optional, can be read from environment variables)
        content_type: Content type for RDF data (optional, auto-detected if not provided)
        batch_size: Number of triples per batch for streaming formats
        stats_callback: Callback function for upload statistics
        store_name: RDFox datastore name (only used with RDFox endpoint type)

    Returns:
        True if the upload was successful
    """
    detected_content_type = content_type or detect_content_type(file_path)

    client = EndpointClient(
        endpoint_url=endpoint,
        endpoint_type=endpoint_type,
        username=username,
        password=password,
        content_type=detected_content_type,
        store_name=store_name,
    )

    reader = get_reader(file_path)

    stats = StatsCollector(file_path)
    if stats_callback:
        stats.set_callback(stats_callback)

    total_triples = await reader.count_triples()
    stats.set_total_triples(total_triples)

    batches = await reader.read_batches(batch_size)
    for batch_content, batch_count in batches:
        _, status_code = await client.upload_data(batch_content, graph)
        stats.update(batch_count, status_code)

    return True


async def upload_rdf_files(
    files: list[Path],
    endpoint: str | None = None,
    endpoint_type: EndpointType = EndpointType.GENERIC,
    graph: str | None = None,
    concurrent_limit: int = 5,
    progress_callback: Callable[[], None] | None = None,
    username: str | None = None,
    password: str | None = None,
    content_type: str | None = None,
    batch_size: int = 100,
    stats_callback: Callable[[dict[str, Any]], None] | None = None,
    store_name: str | None = None,
) -> dict[Path, dict[str, Any]]:
    """
    Upload multiple RDF files to a SPARQL endpoint with concurrency control.

    Args:
        files: List of paths to RDF files to upload
        endpoint: SPARQL endpoint URL (optional, can be read from environment variables)
        endpoint_type: Type of SPARQL endpoint
        graph: Named graph to upload to
        concurrent_limit: Maximum number of concurrent uploads
        progress_callback: Callback function for overall progress
        username: Username for authentication (optional, can be read from environment variables)
        password: Password for authentication (optional, can be read from environment variables)
        content_type: Content type for RDF data (optional, auto-detected if not provided)
        batch_size: Number of triples per batch for streaming formats
        stats_callback: Callback function for upload statistics
        store_name: RDFox datastore name (only used with RDFox endpoint type)

    Returns:
        Dictionary mapping file paths to upload results
    """
    results: dict[Path, dict[str, Any]] = {}
    semaphore = asyncio.Semaphore(concurrent_limit)

    async def upload_with_semaphore(file_path: Path) -> None:
        async with semaphore:
            try:
                await upload_rdf_file(
                    file_path=file_path,
                    endpoint=endpoint,
                    endpoint_type=endpoint_type,
                    graph=graph,
                    username=username,
                    password=password,
                    content_type=content_type,
                    batch_size=batch_size,
                    stats_callback=stats_callback,
                    store_name=store_name,
                )
                results[file_path] = {"success": True}
            except Exception as e:  # noqa: BLE001
                results[file_path] = {
                    "success": False,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }

            if progress_callback:
                progress_callback()

    async with asyncio.TaskGroup() as tg:
        for file_path in files:
            tg.create_task(upload_with_semaphore(file_path))

    return results
