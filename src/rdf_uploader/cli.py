"""Command-line interface for RDF Uploader."""

import asyncio
import os
from pathlib import Path
from typing import Any

import click
import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from rdf_uploader.__about__ import VERSION
from rdf_uploader.endpoints import EndpointType
from rdf_uploader.uploader import upload_rdf_files

app = typer.Typer(help="Upload RDF data to SPARQL endpoints")
console = Console()


@app.command()
def upload(
    files: list[Path] = typer.Argument(
        ..., help="RDF files to upload (N3, Turtle, RDF/XML, etc.)"
    ),
    endpoint: str | None = typer.Option(
        None,
        "--endpoint",
        "-e",
        help="SPARQL endpoint URL (can be read from environment variables)",
    ),
    endpoint_type: EndpointType = typer.Option(
        EndpointType.GENERIC,
        "--type",
        "-t",
        help="Type of SPARQL endpoint",
    ),
    graph: str | None = typer.Option(
        None, "--graph", "-g", help="Named graph to upload to"
    ),
    concurrent: int = typer.Option(
        5, "--concurrent", "-c", help="Maximum number of concurrent uploads"
    ),
    username: str | None = typer.Option(
        None, "--username", "-u", help="Username for authentication"
    ),
    password: str | None = typer.Option(
        None, "--password", "-p", help="Password for authentication"
    ),
    content_type: str | None = typer.Option(
        None,
        "--content-type",
        help="Content type for RDF data (e.g., text/turtle, application/rdf+xml)",
    ),
    batch_size: int = typer.Option(
        1000,
        "--batch-size",
        "-b",
        help="Number of triples per batch for streaming formats",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output showing batch details and server responses",
    ),
    store_name: str | None = typer.Option(
        os.environ.get("RDFOX_STORE_NAME", ""),
        "--store-name",
        "-s",
        help="RDFox datastore name (only used with RDFox endpoint type)",
        envvar="RDFOX_STORE_NAME",
    ),
) -> None:
    """Upload RDF files to a SPARQL endpoint."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(),
        TextColumn("({task.completed}/{task.total})"),
        TextColumn("[cyan]{task.fields[rate]} triples/sec"),
        console=console,
    ) as progress:
        tasks = {}

        def update_stats(stats: dict[str, Any]) -> None:
            file_path = Path(stats["file"])
            if file_path not in tasks:
                tasks[file_path] = progress.add_task(
                    f"Uploading {file_path.name}...",
                    total=stats["total_triples"],
                    rate="0.0",
                )

            progress.update(
                tasks[file_path],
                completed=stats["uploaded_triples"],
                rate=f"{stats['triples_per_second']:.1f}",
            )

            if verbose and "batch_count" in stats and "status_code" in stats:
                console.print(
                    f"[bold cyan]File:[/] {file_path.name} | "
                    f"[bold green]Batch {stats['batch_num']}:[/] {stats['batch_count']} triples | "
                    f"[bold blue]Status:[/] {stats['status_code']}"
                )

        async def run_upload() -> None:
            results = await upload_rdf_files(
                files=files,
                endpoint=endpoint,
                endpoint_type=endpoint_type,
                graph=graph,
                concurrent_limit=concurrent,
                username=username,
                password=password,
                content_type=content_type,
                batch_size=batch_size,
                stats_callback=update_stats,
                store_name=store_name,
            )

            # Display results
            console.print("\nUpload Results:")
            for file_path, result in results.items():
                if isinstance(result, dict) and not result.get("success", False):
                    # Display error details for failed uploads
                    error_type = result.get("error_type", "Unknown error")
                    error_message = result.get("error_message", "No details available")
                    console.print(
                        f"❌ {file_path}: [bold red]{error_type}[/] - {error_message}"
                    )
                else:
                    console.print(f"✅ {file_path}")

        asyncio.run(run_upload())


@app.command()
def version() -> None:
    """Print the version of the RDF Uploader."""
    click.echo(f"RDF Uploader {VERSION}")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
