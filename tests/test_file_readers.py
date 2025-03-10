"""Tests for file reading functionality."""

import pytest

from rdf_uploader.file_readers import (
    LineBasedReader,
    WholeFileReader,
    count_file_lines,
    get_reader,
)


@pytest.mark.asyncio()
async def test_count_lines_turtle(sample_turtle_file):
    """Test counting lines in a Turtle file."""
    line_count = await count_file_lines(sample_turtle_file)
    assert line_count == 8


@pytest.mark.asyncio()
async def test_count_lines_nquads(sample_nq_file):
    """Test counting lines in an N-Quads file."""
    line_count = await count_file_lines(sample_nq_file)
    assert line_count == 500


def test_get_reader_nquads(sample_nq_file):
    """Test getting the correct reader for N-Quads files."""
    reader = get_reader(sample_nq_file)
    assert isinstance(reader, LineBasedReader)


def test_get_reader_turtle(sample_turtle_file):
    """Test getting the correct reader for Turtle files."""
    reader = get_reader(sample_turtle_file)
    assert isinstance(reader, WholeFileReader)


@pytest.mark.asyncio()
async def test_line_based_reader_count_triples(sample_nq_file):
    """Test counting triples in a line-based file."""
    reader = LineBasedReader(sample_nq_file)
    count = await reader.count_triples()
    assert count == 500


@pytest.mark.asyncio()
async def test_line_based_reader_read_batches(sample_nq_file):
    """Test reading batches from a line-based file."""
    reader = LineBasedReader(sample_nq_file)

    # Test with batch size larger than file
    batches = await reader.read_batches(batch_size=900)
    assert len(batches) == 1
    assert batches[0][1] == 500  # 500 triples in the batch

    # Test with smaller batch size
    batches = await reader.read_batches(batch_size=240)
    assert len(batches) == 3
    assert batches[0][1] == 240  # 240 triples in first batch
    assert batches[1][1] == 240  # 260 triples in second batch
    assert batches[2][1] == 20  # 260 triples in second batch


@pytest.mark.asyncio()
async def test_whole_file_reader_count_triples(sample_turtle_file):
    """Test counting triples in a Turtle file."""
    reader = WholeFileReader(sample_turtle_file)
    count = await reader.count_triples()
    # This is an approximation, so we just check it's a reasonable number
    assert count > 0


@pytest.mark.asyncio()
async def test_whole_file_reader_read_batches(sample_turtle_file):
    """Test reading batches from a Turtle file."""
    reader = WholeFileReader(sample_turtle_file)

    # Turtle files are always read as a single batch
    batches = await reader.read_batches(batch_size=100)
    assert len(batches) == 1

    # The content should be the entire file
    content = await reader.read_all()
    assert batches[0][0] == content
