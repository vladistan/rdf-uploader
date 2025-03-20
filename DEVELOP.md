
## Development

### Code Quality

The project uses ruff for linting and formatting:

```bash
# Run linting
ruff check .

# Run formatting
ruff format .
```

### Type Checking

The project uses mypy for type checking:

```bash
mypy src tests
```



## Testing

The project uses pytest for testing. Tests are designed to work with live test databases.

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_uploader.py

# Run with verbose output
pytest -v
```
