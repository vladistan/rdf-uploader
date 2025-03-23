# RDF Uploader

When working with RDF data and multiple triple stores, it is common to need to upload knowledge graphs to different stores. Although most stores claim to be standards-based, there are two main standards: the Graph Store Protocol and SPARQL Update. However, there are nuances regarding exact URL endpoints, named graphs, and authentication, making it a pain to deal with multiple proprietary tools.

Introducing `rdf_uploader`, a single tool that can upload RDF data to a variety of data sources. It is easy to use and has no dependencies on RDFLib or any datastore-specific libraries, relying solely on pure HTTP. With `rdf_uploader`, you can seamlessly upload your RDF data to different triple stores without the hassle of dealing with multiple tools and their quirks.

## Features

- Ingest RDF data into SPARQL endpoints using asynchronous operations
- Support for multiple RDF stores (MarkLogic, Blazegraph, Neptune, RDFox, and Stardog)
- Authentication support for secure endpoints
- Content type detection and customization
- Clear status outputs after each upload operation
- Concurrent uploads with configurable limits

## Installation

### From PyPI

```bash
pip install rdf-uploader
```

## Usage

### Basic Usage

Upload a single RDF file to a SPARQL endpoint:

```bash
rdf-uploader path/to/file.ttl --endpoint http://localhost:3030/dataset/sparql
```

You can also omit the endpoint URL and use environment variables:

```bash
# Set the endpoint URL in an environment variable
export RDF_ENDPOINT=http://localhost:3030/dataset/sparql

# Then run without the --endpoint parameter
rdf-uploader path/to/file.ttl
```

Or specify the endpoint type to use a type-specific environment variable:

```bash
# Set endpoint-specific URL
export MARKLOGIC_ENDPOINT=http://marklogic-server:8000/v1/graphs

# Use the endpoint type to determine which environment variable to use
rdf-uploader path/to/file.ttl --type marklogic
```

### Programmatic Usage

You can also use the library programmatically in your Python code:

```python
from pathlib import Path
from rdf_uploader.uploader import upload_rdf_file
from rdf_uploader.endpoints import EndpointType

# The endpoint URL, username, and password can be provided directly
# or read from environment variables if not specified
await upload_rdf_file(
    file_path=Path("path/to/file.ttl"),
    endpoint="http://localhost:3030/dataset/sparql",
    endpoint_type=EndpointType.GENERIC,
    username="myuser",
    password="mypass"
)

# Using environment variables
# export RDF_ENDPOINT=http://localhost:3030/dataset/sparql
# export RDF_USERNAME=myuser
# export RDF_PASSWORD=mypass
await upload_rdf_file(
    file_path=Path("path/to/file.ttl"),
    endpoint_type=EndpointType.GENERIC
)
```

### Multiple Files

Upload multiple RDF files:

```bash
rdf-uploader upload path/to/file1.ttl path/to/file2.n3 --endpoint http://localhost:3030/dataset/sparql
```

### Specify Endpoint Type

```bash
rdf-uploader upload path/to/file.ttl --endpoint http://localhost:3030/dataset/sparql --type fuseki
```

Available endpoint types:
- `marklogic`
- `neptune`
- `blazegraph`
- `rdfox`
- `stardog`

### Specify Named Graph

```bash
rdf-uploader upload path/to/file.ttl --endpoint http://localhost:3030/dataset/sparql --graph http://example.org/graph
```

### Authentication

For endpoints that require authentication:

```bash
rdf-uploader upload path/to/file.ttl --endpoint http://localhost:3030/dataset/sparql --username myuser --password mypass
```

You can also set authentication credentials using environment variables:

```bash
export RDF_USERNAME=myuser
export RDF_PASSWORD=mypass
rdf-uploader upload path/to/file.ttl --endpoint http://localhost:3030/dataset/sparql
```

For endpoint-specific credentials, use the endpoint type as a prefix:

```bash
export MARKLOGIC_USERNAME=mluser
export MARKLOGIC_PASSWORD=mlpass
rdf-uploader upload path/to/file.ttl --endpoint http://marklogic-server:8000/v1/graphs --type marklogic
```

### Content Type

Specify the content type for the RDF data:

```bash
rdf-uploader upload path/to/file.ttl --endpoint http://localhost:3030/dataset/sparql --content-type "text/turtle"
```

If not specified, the content type is automatically detected based on the file extension:
- `.ttl`, `.turtle`: `text/turtle`
- `.nt`: `application/n-triples`
- `.n3`: `text/n3`
- `.nq`, `.nquads`: `application/n-quads`
- `.rdf`, `.xml`: `application/rdf+xml`
- `.jsonld`: `application/ld+json`
- `.json`: `application/rdf+json`
- `.trig`: `application/trig`

### Control Concurrency

Limit the number of concurrent uploads:

```bash
rdf-uploader upload path/to/*.ttl --endpoint http://localhost:3030/dataset/sparql --concurrent 10
```

### Verbose Mode

Enable verbose output to see detailed information about each batch upload, including the number of triples per batch and server response codes:

```bash
rdf-uploader upload path/to/file.ttl --endpoint http://localhost:3030/dataset/sparql --verbose
```

### Help

Get help on available commands and options:

```bash
rdf-uploader --help
rdf-uploader upload --help
```


### Environment Variables

You can configure the RDF Uploader using environment variables, which is especially useful for CI/CD pipelines or when working with multiple endpoints. The library also supports reading values from a `.envrc` file in the current working directory if environment variables are not set:

#### Endpoint URLs

```bash
# Generic endpoint URL
export RDF_ENDPOINT=http://localhost:3030/dataset/sparql

# Endpoint-specific URLs
export MARKLOGIC_ENDPOINT=http://marklogic-server:8000/v1/graphs
export NEPTUNE_ENDPOINT=https://your-neptune-instance.amazonaws.com:8182/sparql
export BLAZEGRAPH_ENDPOINT=http://blazegraph-server:9999/blazegraph/sparql
export RDFOX_ENDPOINT=http://rdfox-server:12110/datastores/default/content
export STARDOG_ENDPOINT=https://your-stardog-instance:5820/database
```

#### Authentication

```bash
# Generic credentials
export RDF_USERNAME=myuser
export RDF_PASSWORD=mypass

# Endpoint-specific credentials
export MARKLOGIC_USERNAME=mluser
export MARKLOGIC_PASSWORD=mlpass
export NEPTUNE_USERNAME=neptuneuser
export NEPTUNE_PASSWORD=neptunepass
export BLAZEGRAPH_USERNAME=bguser
export BLAZEGRAPH_PASSWORD=bgpass
export RDFOX_USERNAME=rdfoxuser
export RDFOX_PASSWORD=rdfoxpass
export STARDOG_USERNAME=sduser
export STARDOG_PASSWORD=sdpass
```

#### RDFox Store Name

```bash
export RDFOX_STORE_NAME=mystore
```

### Test Configuration

Tests use a local SPARQL endpoint by default. You can configure the test endpoint by setting environment variables:

```bash
export TEST_ENDPOINT_URL=http://localhost:3030/test
export TEST_ENDPOINT_TYPE=fuseki
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
