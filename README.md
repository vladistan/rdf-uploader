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


### Test Configuration

Tests use a local SPARQL endpoint by default. You can configure the test endpoint by setting environment variables:

```bash
export TEST_ENDPOINT_URL=http://localhost:3030/test
export TEST_ENDPOINT_TYPE=fuseki
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
