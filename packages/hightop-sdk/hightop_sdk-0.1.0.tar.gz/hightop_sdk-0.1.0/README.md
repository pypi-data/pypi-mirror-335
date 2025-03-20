# Hightop SDK

A Python SDK for the Hightop API.

## Installation

```bash
pip install hightop-sdk
```

## Usage

### Basic Setup

```python
from hightop_sdk import HightopSDK

# Initialize the SDK with your API key
sdk = HightopSDK(api_key="your_api_key_here")

# Make API calls using the SDK
response = sdk.your_api_endpoint()
```

### Configuration

You can configure the SDK with various options:

```python
from hightop_sdk import HightopSDK, Configuration

# Create a custom configuration
config = Configuration(
    api_key="your_api_key_here",
    host="https://api.hightop.com/api",  # Optional: customize API host
    timeout=30  # Optional: set request timeout
)

# Initialize SDK with custom configuration
sdk = HightopSDK(configuration=config)
```

### Error Handling

The SDK includes built-in error handling for common API errors:

```python
from hightop_sdk.exceptions import ApiException

try:
    response = sdk.your_api_endpoint()
except ApiException as e:
    print(f"API Error: {e.status} - {e.reason}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

### Response Handling

API responses are automatically deserialized into Python objects:

```python
# Example response handling
response = sdk.your_api_endpoint()
data = response.data  # Access the deserialized response data
```

## Examples

### Making API Requests

```python
# Example of making a GET request
response = sdk.get_data()

# Example of making a POST request with data
data = {
    "name": "Example",
    "value": 123
}
response = sdk.create_data(data)

# Example of making a request with query parameters
response = sdk.search_data(query="example", limit=10)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
