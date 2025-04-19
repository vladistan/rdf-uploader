FROM python:3.12-slim

ARG VERSION=0.15.0
RUN pip install --no-cache-dir rdf-uploader==${VERSION}

ENTRYPOINT ["rdf-uploader"]
