# RDF Uploader



Knowledge graph developers often need to work with various types of triple stores within the same projects. Each store has its own way of handling endpoints, authentication, and named graphs, which can complicate the upload process. RDF Uploader addresses this by offering a consistent interface for popular stores like MarkLogic, Blazegraph, Neptune, RDFox, and Stardog. Unlike typical RDFLib-based applications, such as those using RDFLib's `Graph` class that upload one triple at a time, RDF Uploader supports batch uploads and concurrency. This approach prevents server overload from large files, unlike using CURL, which might crash the server by dumping an entire multi-gigabyte file at once. Concurrency also boosts performance in clustered triple store environments by allowing multiple uploads simultaneously. While many stores offer high-throughput loading methods, these are often unique to each store and require direct server access to load from local files. RDF Uploader, using simple HTTP requests, avoids these complexities and dependencies, making it lightweight and easy to integrate into existing workflows, while eliminating the hassle of dealing with different endpoint implementations.

![License MIT](https://img.shields.io/github/license/vladistan/rdf-uploader)

![Demo GIF](docs/images/demo.gif)

## Table of Contents
- [Features](#features)
- [Installation & Quick Start](#installation--quick-start)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Command Line Reference](#command-line-reference)
- [Environment Variables](#environment-variables)
- [Programmatic Usage](#programmatic-usage)
- [License](#license)

## Features

- Ingest RDF data into SPARQL endpoints using asynchronous operations
- Support for multiple RDF stores (MarkLogic, Blazegraph, Neptune, RDFox, and Stardog)
- Authentication support for secure endpoints
- Content type detection and customization
- Concurrent uploads with configurable limits
- Batching of RDF statements for efficient processing
- Verbose output for detailed logging
- Support for named graphs


## Installation & Quick Start

**Choose your preferred method:**

### pip
```bash
pip install rdf-uploader
rdf-uploader file.ttl --endpoint http://localhost:3030/dataset/sparql
```

### pipx (without permanent installation)
```bash
pipx run rdf-uploader upload file.ttl --endpoint http://localhost:3030/dataset/sparql
```

### Docker
```bash
docker run -v $(pwd):/data vladistan/rdf-uploader:latest /data/file.ttl --endpoint http://localhost:3030/dataset/sparql
```

### With Environment Variables
```bash
export RDF_ENDPOINT=http://localhost:3030/dataset/sparql
rdf-uploader file.ttl
```

### With .envrc File
Create `.envrc` with your configuration, then run:
```bash
# .envrc file content
export RDF_ENDPOINT="http://localhost:3030/dataset/sparql"

# Command to run
rdf-uploader file.ttl
```

## Usage Guide

### Basic Operations

**Upload a single file:**
```bash
rdf-uploader file.ttl --endpoint http://localhost:3030/dataset/sparql
```

**Upload multiple files:**
```bash
rdf-uploader file1.ttl file2.n3 --endpoint http://localhost:3030/dataset/sparql
```

**Use a named graph:**
```bash
rdf-uploader file.ttl --endpoint http://localhost:3030/dataset/sparql --graph http://example.org/graph
```

### Authentication

**With credentials:**
```bash
rdf-uploader file.ttl --endpoint http://localhost:3030/dataset/sparql --username myuser --password mypass
```

### Content Types & Format

**Explicitly specify content type:**
```bash
rdf-uploader file.ttl --content-type "text/turtle"
```

**Supported formats** (auto-detected by extension):
- `.ttl`, `.turtle`: `text/turtle`
- `.nt`: `application/n-triples`
- `.n3`: `text/n3`
- `.nq`, `.nquads`: `application/n-quads`
- `.rdf`, `.xml`: `application/rdf+xml`
- `.jsonld`: `application/ld+json`
- `.json`: `application/rdf+json`
- `.trig`: `application/trig`

### Performance Options

**Control concurrency:**
The `--concurrent` option allows you to specify the number of concurrent upload operations. For example, using `--concurrent 10` will enable the uploader to process up to 10 files simultaneously, which can significantly speed up the upload process when dealing with multiple files.

```bash
rdf-uploader *.ttl --concurrent 10
```

**Enable verbose output:**
The `--verbose` option provides detailed output during the upload process. This can be useful for debugging or monitoring the progress of the upload, as it will display additional information about each step the uploader takes.

```bash
rdf-uploader file.ttl --verbose
```

**Set batch size:**
The `--batch-size` option lets you define the number of RDF statements to be included in each batch during the upload. For instance, `--batch-size 5000` will group the RDF data into batches of 5000 statements, which can help manage memory usage and optimize performance for large datasets.

```bash
rdf-uploader file.ttl --batch-size 5000
```

## Configuration

RDF Uploader offers three ways to configure parameters, with the following priority:

1. **Command-line arguments** (highest priority)
2. **Environment variables** (checked if CLI args not provided)
3. **.envrc file** (checked if environment variables not set)

### Endpoint Types

The tool supports these endpoints with optimized handling:

- `marklogic`
- `neptune`
- `blazegraph`
- `rdfox`
- `stardog`
- `generic` (default)

Specify the endpoint type:
```bash
rdf-uploader file.ttl --type stardog
```

### Endpoint-specific Variables

When an endpoint type is specified, type-specific variables take precedence:

```bash
# Generic endpoint (fallback)
export RDF_ENDPOINT=http://localhost:3030/dataset/sparql

# Type-specific endpoint (takes precedence when --type marklogic is used)
export MARKLOGIC_ENDPOINT=http://marklogic-server:8000/v1/graphs
```

## Command Line Reference

### Basic Syntax

```bash
rdf-uploader [OPTIONS] FILES...
```

### Options Reference

| Category | Option | Short | Description | Default |
|----------|--------|-------|-------------|---------|
| **Files** | `FILES...` | | One or more RDF files to upload | (required) |
| **Endpoint** | `--endpoint` | `-e` | SPARQL endpoint URL | (required) |
| | `--type` | `-t` | Endpoint type | `generic` |
| | `--graph` | `-g` | Named graph to upload to | Default graph |
| | `--store-name` | `-s` | RDFox datastore name | (required for RDFox) |
| **Auth** | `--username` | `-u` | Username | |
| | `--password` | `-p` | Password | |
| **Content** | `--content-type` | | Content type for RDF data | Auto-detected |
| **Performance** | `--concurrent` | `-c` | Max concurrent uploads | 5 |
| | `--batch-size` | `-b` | Triples per batch | 1000 |
| **Output** | `--verbose` | `-v` | Enable detailed output | `False` |

## Environment Variables

### General Configuration

```bash
# Generic endpoint URL and auth
export RDF_ENDPOINT=http://localhost:3030/dataset/sparql
export RDF_USERNAME=myuser
export RDF_PASSWORD=mypass
```

### Endpoint-specific Configuration

```bash
# MarkLogic
export MARKLOGIC_ENDPOINT=http://marklogic-server:8000/v1/graphs
export MARKLOGIC_USERNAME=mluser
export MARKLOGIC_PASSWORD=mlpass

# Neptune
export NEPTUNE_ENDPOINT=https://your-neptune-instance.amazonaws.com:8182/sparql
export NEPTUNE_USERNAME=neptuneuser
export NEPTUNE_PASSWORD=neptunepass

# Blazegraph
export BLAZEGRAPH_ENDPOINT=http://blazegraph-server:9999/blazegraph/sparql
export BLAZEGRAPH_USERNAME=bguser
export BLAZEGRAPH_PASSWORD=bgpass

# RDFox
export RDFOX_ENDPOINT=http://rdfox-server:12110/datastores/default/content
export RDFOX_USERNAME=rdfoxuser
export RDFOX_PASSWORD=rdfoxpass
export RDFOX_STORE_NAME=mystore

# Stardog
export STARDOG_ENDPOINT=https://your-stardog-instance:5820/database
export STARDOG_USERNAME=sduser
export STARDOG_PASSWORD=sdpass
```

## Programmatic Usage

Use the library in your Python code:

```python
from pathlib import Path
from rdf_uploader.uploader import upload_rdf_file
from rdf_uploader.endpoints import EndpointType

# With explicit parameters
await upload_rdf_file(
    file_path=Path("file.ttl"),
    endpoint="http://localhost:3030/dataset/sparql",
    endpoint_type=EndpointType.GENERIC,
    username="myuser",
    password="mypass"
)

# Using environment variables
await upload_rdf_file(
    file_path=Path("file.ttl"),
    endpoint_type=EndpointType.GENERIC
)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
