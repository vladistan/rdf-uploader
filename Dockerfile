FROM python:3.12-slim

ARG VERSION=latest
RUN pip install rdf-uploader==${VERSION}

ENTRYPOINT ["rdf-uploader"]
