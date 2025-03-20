# dorky

[![PyPI - Version](https://img.shields.io/pypi/v/dorky.svg)](https://pypi.org/project/dorky)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dorky.svg)](https://pypi.org/project/dorky)

A secure and flexible key management system for storing and managing service credentials.

## Installation

```console
pip install dorky
```

## Usage

### Basic Usage

```python
from dorky import create_key
from dorky.impl.jsonfile import JsonBasedDorkyService

# Initialize the service with JSON file storage
service = JsonBasedDorkyService("keys.json")

# Create a new key
key = service.create_key(
    username="john_doe",
    service_name="my-service",
    key_id="my-service-main"  # optional
)

# Verify a key
is_valid = service.verify_key_str(key.encode())

# List all keys
all_keys = service.list_keys()

# List keys for a specific service
my_service_keys = service.list_keys(service_name="my-service")

# List keys for a specific user
user_keys = service.list_keys(username="john_doe")

# Delete a key
service.delete_key(key)
```

### Using SQLite Storage

```python
from dorky.impl.sqlite import SqliteBasedDorkyService

# Initialize the service with SQLite storage
service = SqliteBasedDorkyService("keys.db")

# Use the same interface as JSON storage
key = service.create_key("john_doe", service_name="my-service")
```

### Key Format

Keys are stored in the following format:
```
service_name:username:key_id:password
```

The password is securely hashed using scrypt (default) or PBKDF2 before storage.

## Development

### Running Tests

```console
pytest tests/
```

## License

`dorky` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
