# transend-python

![Python Tests](https://github.com/TranstarIndustries/transend-python/workflows/Python%20Tests/badge.svg)
![PyPI Version](https://img.shields.io/pypi/v/transend.svg)
![PyPI Downloads](https://img.shields.io/pypi/dm/transend.svg)

Python Client for the Transend APIs

## Installation

### From PyPI (Recommended)

```bash
pip install transend
```

### From Source

```bash
# Clone the repository
git clone https://github.com/TranstarIndustries/transend-python.git
cd transend-python

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

```python
from src.client import TransendAPIClient

# Initialize with your API credentials
api_key = "your_api_key_here"
api_token = "your_api_token_here"
client = TransendAPIClient(api_key, api_token)

# Example calls
sort_types = client.product.get_all_sort_types()
branches = client.branch.get_all_branches()
dtcs = client.vehicle.get_all_dtcs()
print(sort_types, branches, dtcs)

# Vehicle lookup
vhid = client.vehicle.get_year_make_model_vhid(2010, "Toyota", "Camry")
vehicle = client.vehicle.get_vehicle_by_vhid(vhid["vhid"])
print(vehicle)
```

## Available APIs

- **ProductAPI**: Access product information, sorting options, and tags
- **BranchAPI**: Get branch details and listings
- **VehicleAPI**: Look up vehicles by VIN, year/make/model, and access vehicle details
- **AccountAPI**: Manage customer accounts, bank accounts, and credit cards
- **ContentAPI**: Retrieve articles and resources
- **CoreAPI**: Access core information
- **CustomerAPI**: Get user information

## Running Tests

We use pytest for testing. To run the tests:

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run a specific test file
python -m pytest tests/test_vehicle_api.py

# Run with coverage report
python -m pytest --cov=src --cov-report=term
```

## Continuous Integration

This project uses GitHub Actions to automatically run tests on every push and pull request.
The workflow runs tests on multiple Python versions (3.8, 3.9, 3.10, 3.11) to ensure compatibility.

You can view the test results in the "Actions" tab of the GitHub repository.

## Release Process

This package uses GitHub Actions to automatically publish to PyPI when a new release is created:

1. Update the version number in `setup.py`
2. Create a new release on GitHub:
   - Go to the repository's "Releases" section
   - Click "Draft a new release"
   - Choose or create a tag in the format `v{version}` (e.g., `v0.1.0`)
   - Add a title and release notes
   - Click "Publish release"
3. The GitHub Actions workflow will automatically:
   - Build the package
   - Verify the package contents
   - Upload the package to PyPI

### Setting up PyPI publishing

For the PyPI publishing to work, a PyPI API token needs to be added to the repository secrets:

1. Create an API token in your PyPI account settings
2. Add the token as a repository secret named `PYPI_API_TOKEN` in your GitHub repository settings
