#!/bin/bash

# Get the version from the command line argument
VERSION=${1:-latest}

# Print the version being used
echo "Building Docker image for version: $VERSION"

# Set the version as a build argument
BUILD_ARGS="--build-arg VERSION=$VERSION"
docker build -t vladistan/rdf-uploader:$VERSION $BUILD_ARGS .
