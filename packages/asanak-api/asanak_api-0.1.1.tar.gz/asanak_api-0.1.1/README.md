# Asanak API

[![PyPI version](https://img.shields.io/pypi/v/asanak-api.svg)](https://pypi.org/project/asanak-api/0.1.0/)
[![Python versions](https://img.shields.io/pypi/pyversions/asanak-api.svg)](https://pypi.org/project/asanak-api/0.1.0/)

A Python client library for the Asanak SMS API. This package provides a simple and intuitive interface to interact with Asanak SMS services.

## Installation

You can install the package via pip:

```bash
pip install asanak-api
```

## Quick Start

```python
from asanak_api import AsanakAPI

# Initialize the client
api = AsanakAPI(username="your_username", password="your_password")

# Or use the API key format (username,password)
# api = AsanakAPI(api_key="your_username,your_password")

# Send an SMS
response = api.sms_send({
    "source": "your_source_number",
    "destination": ["destination_number1", "destination_number2"],
    "message": "Hello from Asanak API!"
})

print(response)
```

## Authentication

Asanak SMS provider uses username and password for authentication. You can provide these credentials in two ways:

1. **Separate username and password parameters**:
   ```python
   api = AsanakAPI(username="your_username", password="your_password")
   ```

2. **Combined API key**:
   ```python
   api = AsanakAPI(api_key="your_username,your_password")
   ```

## Available Methods

### SMS Operations

- **Send SMS**:
  ```python
  api.sms_send({
      "source": "your_source_number",
      "destination":"recipient_number1,recipient_number2,...",
      "message": "Your message content"
  })
  ```

- **Send Template SMS**:
  ```python
  api.sms_template({
      "source": "your_source_number", 
      "destination": "recipient_number1,recipient_number2,...",
      "message": "Your template name",
      "variables": {"var1": "value1", "var2": "value2"}
  })
  ```

- **Send Peer-to-Peer SMS**:
  ```python
  api.sms_p2p(
    {
        {
      "source": "your_source_number",
      "destinations": "recipient_number1",
      "messages": "Message for recipient1"
        },
        {
      "source": "your_source_number",
      "destinations": "recipient2",
      "messages": "Message for recipient2"
        }
    }
  )
  ```

- **Check SMS Status**:
  ```python
  api.sms_status({"msgid": "your_message_id"})
  ```

### Other Operations

- **Get Templates List**:
  ```python
  api.sms_template_list()
  ```

- **Get Credit**:
  ```python
  api.get_credit()
  ```

- **Get Rial Credit**:
  ```python
  api.get_rial_credit()
  ```

## Response Format

All API methods return responses in the following format:

```python
{
    "status": status_code,    # Status code of the response
    "message": "message",     # Message describing the status
    "data": {...}             # Response data
}
```

## Status Codes

The library includes predefined status codes that help you interpret API responses:

- SMS Status codes - Available in `SMS_STATUS` dictionary
- API Status codes - Available in `API_STATUS` dictionary

## Exception Handling

The library can raise the following exceptions:

- `APIException`: For API-related errors
- `HTTPException`: For HTTP connection issues

```python
from asanak_api import AsanakAPI, APIException, HTTPException

try:
    api = AsanakAPI(api_key="your_api_key")
    response = api.sms_send({...})
except APIException as e:
    print(f"API Error: {e}")
except HTTPException as e:
    print(f"HTTP Error: {e}")
```

## Requirements

- Python >= 3.12
- requests >= 2.32.3


