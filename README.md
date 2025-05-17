# RDF Uploader

A tool for uploading RDF data to different types of triple stores
with consistent behavior across different endpoint types.

![RDF Uploader Demo](docs/images/demo.gif)


[![PyPI - Version](https://img.shields.io/pypi/v/rdf-uploader)](https://pypi.org/project/rdf-uploader/)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/vladistan/rdf-uploader?label=docker)](https://hub.docker.com/r/vladistan/rdf-uploader)
![Tests](https://github.com/vladistan/rdf-uploader/actions/workflows/ci.yaml/badge.svg?event=push&branch=main)
[![codecov](https://codecov.io/github/vladistan/rdf-uploader/graph/badge.svg?token=KGUVQW05BC)](https://codecov.io/github/vladistan/rdf-uploader)
[![Python Version](https://img.shields.io/pypi/pyversions/rdf-uploader)](https://pypi.org/project/rdf-uploader/)
[![License MIT](https://img.shields.io/github/license/vladistan/rdf-uploader)](https://github.com/vladistan/rdf-uploader/blob/main/LICENSE)


Recently, I've been working extensively with knowledge graphs, which
often involves work with different types of triple stores like MarkLogic,
Blazegraph, RDFox,AWS Neptune, and StarDog at the same time. Each
store comes with a different bulk-loading process, its own endpoint
URLs, authentication rules, and named-graph conventions. Dealing
with those differences became very tedious very quickly.


To get rid of the tedium, I built **RDF-Uploader** — a tool
that streamlines the workflow and offers a consistent, high-performance
method for uploading large RDF datasets.



## Table of Contents
- [RDF Uploader](#rdf-uploader)
  - [Table of Contents](#table-of-contents)
  - [Rationale](#rationale)
  - [Features](#features)
  - [Installation \& Quick Start](#installation--quick-start)
    - [pip](#pip)
    - [pipx (without permanent installation)](#pipx-without-permanent-installation)
    - [Homebrew](#homebrew)
    - [Docker](#docker)
    - [With Environment Variables](#with-environment-variables)
    - [With .envrc File](#with-envrc-file)
  - [Usage Guide](#usage-guide)
    - [Basic Operations](#basic-operations)
    - [Authentication](#authentication)
    - [Content Types \& Format](#content-types--format)
    - [Performance Options](#performance-options)
  - [Configuration](#configuration)
  - [Command Line Options Reference](#command-line-options-reference)
  - [Environment Variables](#environment-variables)
    - [General Configuration](#general-configuration)
    - [Endpoint-specific Configuration](#endpoint-specific-configuration)
- [Using .envrc file](#using-envrc-file)
  - [Programmatic Usage](#programmatic-usage)
  - [License](#license)

## Rationale


To understand why uploading to RDF stores is annoying, lets look at different methods
to do it.

 - Use RDFLib’s `store.update` method.

    This approach relies on the standard [SPARQL Update
    protocol](https://www.w3.org/TR/sparql11-update/),
    so it will usually work with any triple store. However, it is
    the slowest option. The simplest usage pattern is easy to write;
    however, calling [`store.update`](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.plugins.stores.html#rdflib.plugins.stores.memory.Memory.update) in a loop for one triple at a time is
    painfully inefficient. Stores like [AWS Neptune](https://aws.amazon.com/neptune/)
    take roughly the same time to ingest a single triple as they do a batch of a
    thousand, and the difference is even greater with high-performance
    engines such as RDFox.

  - Use proprietary method recommended by the store.

    Most triple stores implement their own proprietary bulk-loading tools, and they’re usually far
    faster than looping over RDFLib’s `store.update`. The catch is that every vendor does it
    differently. AWS Neptune, for example, [ingests data from an S3 bucket](https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load.html), while
    Blazegraph expects a file that already lives on the [server's local disk](https://github.com/blazegraph/database/wiki/Bulk_Data_Load).

    When your project has to target several stores at once, juggling these loader-specific
    workflows quickly becomes painful. Each path demands extra code to stage the files—either
    uploading to S3 or copying them onto the server—and each path requires additional permissions
    for developers and CI pipelines. In many organizations, granting that level of access simply
    isn’t feasible.

  - Use CURL to post data to a bulk endpoint

	Almost all triple stores provide an HTTP endpoint for bulk loading data.  Either via standard
	[Graph Store Protocol](https://www.w3.org/TR/sparql11-http-rdf-update/) or
    through some proprietary means like [Stardog's CLI](https://docs.stardog.com/operating-stardog/database-administration/adding-data#adding-data-via-the-cli).   This method is performant and doesn't
	require setting up any special access.  However,  there are a few challenges to this method as
	well.  First, the actual implementation of the endpoint is different for different stores. Some
	support the standard protocols, some implement their own.  Second, using CURL implies loading
	all the data in a single transaction.  This is OK when the dataset is rather small, but all the
	stores have a limit of how much data they could receive at a time.  For some stores this limit
	is pretty large, but nevertheless it is always finite and always much smaller that the limit
	of the number of triples the store can handle.  Also, if an error occurs during the batch upload
	of a very large data block the entire transaction has to be repeated.

	The later limitation can be mitigated by splitting the dataset into smaller parts and posting them
	to the triple store separately.  But this has to be done either manually through tedious and
	error prone process, or by developing a complex program to automate the splitting.


To make the data loading experience less annoying, I created this tool.
It combines the advantages of the above methods while eliminating their downsides.


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

### Homebrew

The homebrew formula for `rdf-uploader` lives in the private tap `vladistan/homebrew-gizmos`
This separate tap is required because the package is still new and hasnt yet met the popularity and
stability thresholds for inclusion in `homebrew-core`. Use the following commands to install it
from the private tap.


```bash
brew tap vladistan/homebrew-gizmos
brew install rdf-uploader

# Quick test
rdf-uploader file.ttl --endpoint http://localhost:3030/dataset/sparql
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

To upload a single file just specify it's name, endpoint URL and the
endpoint type

```bash
rdf-uploader upload file.ttl --endpoint http://localhost:3030/dataset/sparql --type blazegraph
```
The following endpoint types are supported

- `marklogic`
- `neptune`
- `blazegraph`
- `rdfox`
- `stardog`
- `generic` (default)

**Upload multiple files:**

You can upload multiple files at once

```bash
rdf-uploader upload file1.ttl file2.n3 --endpoint http://localhost:3030/dataset/sparql --type blazegraph
```

**Use a named graph:**

If you need to upload to a specific named graph, you can use   `--graph` option.

```bash
rdf-uploader upload poke-a.nq --endpoint https://crystalia.us-east-1.neptune.amazonaws.com:8182/sparql  --type neptune  --graph urn:default
```

### Authentication

**With credentials:**

If the store requires authentication, you can pass them on a command
line

```bash
rdf-uploader upload file.ttl --endpoint http://localhost:3030/dataset/sparql --username myuser --password mypass
```
However, it is better to configure credentials using configuration file
or environment variables (see below)

### Content Types & Format

Normally, the tool tries to determine the content type of the file.
Below is the list of recognized content types and extensions.

**Supported formats**

- `.ttl`, `.turtle`: `text/turtle`
- `.nt`: `application/n-triples`
- `.n3`: `text/n3`
- `.nq`, `.nquads`: `application/n-quads`
- `.rdf`, `.xml`: `application/rdf+xml`
- `.jsonld`: `application/ld+json`
- `.json`: `application/rdf+json`
- `.trig`: `application/trig`

**Explicitly specify content type:**

You can also specify the content type explicitly

```bash
rdf-uploader upload file.ttl --content-type "text/turtle"
```

### Performance Options

**Control concurrency:**

The `--concurrent` option allows you to specify the number of
concurrent upload operations. For example, using `--concurrent 10`
will enable the uploader to process up to 10 files simultaneously,
which can significantly speed up the upload process when dealing
with multiple files.

```bash
rdf-uploader upload *.ttl --concurrent 10
```

**Enable verbose output:**


The `--verbose` option provides detailed output during the upload process. This can be useful for debugging or monitoring the progress of the upload, as it will display additional information about each step the uploader takes.

```bash
rdf-uploader upload file.ttl --verbose
```

**Set batch size:**

The `--batch-size` option lets you define the number of RDF statements
to be included in each batch during the upload. For instance,
`--batch-size 5000` will group the RDF data into batches of 5000
statements, which can help manage memory usage and optimize performance
for large datasets.

```bash
rdf-uploader upload file.ttl --batch-size 5000
```

## Configuration

RDF Uploader offers three ways to configure parameters, with the
following priority:

1. **Command-line arguments** (highest priority)
2. **Environment variables** (checked if CLI args not provided)
3. **.envrc file** (checked if environment variables not set)


## Command Line Options Reference


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

Frequently used options can be put in the environment variables, thus
making your CLI commands much shorter and reducing the risk of exposing
credentials

RDF Uploader supports two categories of environment variables:
generic and endpoint-specific. Endpoint-specific variables (prefixed
with the endpoint type, like `MARKLOGIC_ENDPOINT`) are tailored to
particular triple store implementations and are checked first. If
these specific variables aren't found, the uploader falls back to
generic variables (prefixed with `RDF_`, like `RDF_ENDPOINT`) which
apply to all endpoint types. This hierarchical approach allows you
to configure default credentials and parameters while maintaining
the ability to override settings for specific endpoint types when
needed.

Below is the list of recognized environment variables

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

# Using .envrc file

For a more convenient development workflow, you can use a `.envrc` file to store your environment variables. This is especially useful when working with multiple projects that require different configurations.

The `.envrc` file should be placed in your project's root directory. When using RDF Uploader, it will automatically look for this file and load the variables if neither command-line options nor environment variables are set.

Example `.envrc` file:

```
export RDF_ENDPOINT=http://localhost:3030/dataset/sparql
export RDF_USERNAME=myuser
export RDF_PASSWORD=mypass

# MarkLogic configuration
export MARKLOGIC_ENDPOINT=http://marklogic-server:8000/v1/graphs
export MARKLOGIC_USERNAME=mluser
export MARKLOGIC_PASSWORD=mlpass

# Performance options
export RDF_BATCH_SIZE=10000
export RDF_WORKERS=4
export RDF_TIMEOUT=300

```


## Programmatic Usage

Instead of using `RDF-Uploader` as a CLI tool you can directly integrate
it to your Python project This allows you
to programmatically upload RDF files as they are being generated by your
code.  Like the CLI tool the library method accepts parameters either
explicitly or indirectly from the environment variables.


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

---

⭐️ If you find this repository helpful, please consider giving it a star!

Keywords: RDF, Knowledge Graphs, Graph Databases, AI, Triple Stores
