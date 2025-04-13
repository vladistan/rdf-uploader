#!/bin/bash

# Check if git worktree is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "Error: Git working directory is not clean."
    echo "Please commit or stash your changes before building and publishing."
    exit 1
fi

# Get the version from the command line argument
if [ -z "$1" ]; then
    echo "Error: Version is required"
    echo "Usage: $0 <version>"
    exit 1
fi
VERSION=$1

# Print the version being used
echo "Building and publishing package for version: $VERSION"

rm -rf dist venv

SAVED_BRANCH=$(git branch --show-current)
git checkout v$VERSION

uv venv --python 3.12 --extra dev
source .venv/bin/activate

echo "VERSION = \"${VERSION}.0\"" > src/rdf_uploader/__about__.py

uv sync
uv build

hatch publish

git reset --hard

rm -rf dist .venv uv.lock
git checkout $SAVED_BRANCH
