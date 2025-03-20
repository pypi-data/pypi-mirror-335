# Simple Currency Converter

A simple Python package for currency conversion using the [Currency API](https://github.com/fawazahmed0/currency-api).

## Installation

```bash
pip install simple_currency_converter
```

## Usage

### As a Python module

```python
from simple_currency_converter import convert

# Convert 100 USD to AUD
result = convert("usd", "aud", 100)
print(f"100 USD = {result:.2f} AUD")
```

### Available currencies

You can access currency code dictionaries:

```python
from simple_currency_converter import common_codes, crypto_codes, all_codes

# Print available common currencies
print(common_codes)
```

### As a command-line tool

Basic conversion:
```bash
currency-convert usd aud 100
```

This will output something like:
```
100.0 USD = 152.34 AUD
```

List available currencies:
```bash
# List common currencies
currency-convert --list-common

# List cryptocurrency codes
currency-convert --list-crypto

# List all supported currencies
currency-convert --list-all
```

## Development

### Running tests

The project includes a comprehensive test suite using pytest. To run the tests:

1. Clone the repository
2. Install the package in development mode:

```bash
# Install package in development mode
pip install -e .

# Install test dependencies
pip install pytest pytest-cov
```

3. Run the tests:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=simple_currency_converter
```

### GitHub Actions

This project uses GitHub Actions for continuous integration. Tests are automatically run on push and pull requests to the main branch, across multiple Python versions.

## License

MIT
