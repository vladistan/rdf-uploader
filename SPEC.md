# RDF Uploader Project Specification

## Introduction
- **Project Name**: RDF Uploader
- **Purpose**:
  The RDF Uploader is a tool that streamlines transferring RDF data (e.g., N3 and Turtle) to SPARQL endpoints through a simple CLI.

## Features
- **Core Functionality**:
  - Ingest RDF data into SPARQL endpoints using asynchronous operations.
  - Accommodate multiple RDF stores for broader interoperability.
  - Provide clear status outputs after each upload operation.
- **Supported Formats**:
  - N3
  - Turtle

/// Start of Selection
## Technical Requirements
- **Programming Language**: Use Python for all functionality. Ensure that the code is clear, modular, and compatible with at least Python 3.11 while remaining valid for future Python 3.x releases.
- **CLI Framework**: Employ Typer to implement command-line functionality. Provide subcommands, arguments, and automatic help text generation.
- **Concurrency**: Utilize asyncio for all asynchronous operations. Include clear task scheduling and event loop management for network-bound or I/O-bound tasks.
- **HTTP Client**: Use httpx. Ensure straightforward handling of asynchronous HTTP requests and responses. Demonstrate error handling at the request level.
- **Type Annotations**: Include complete Python type annotations for functions, classes, and modules. This is necessary for improved code clarity, static analysis, and LLM-based code comprehension.
- **Python Version**: Confirm that the implementation runs without modification on standard Python distributions. Avoid platform-specific dependencies that could hinder portability.

## Testing
- **Unit Tests**:
  - Use live test databases.
  - Employ test graphs with predictable triple structures for easy cleanup.
  - Avoid mocking; test with real data.

## Error Handling
- **Approach**:
  - Directly throw errors to the user, as this is a developer tool.

## Documentation
- **README**:
  - Include detailed instructions on setup, usage, and testing.

## Future Enhancements
- **Database Type Detection**:
  - Implement automatic detection of database types in future versions.
