import pytest
from dorky.helper import generate_key_id, generate_random_password, create_key
from dorky.types import PlainKeyContent

def test_generate_key_id():
    # Test that key_id is a hex string of length 8 (4 bytes = 8 hex chars)
    key_id = generate_key_id()
    assert isinstance(key_id, str)
    assert len(key_id) == 8
    assert all(c in '0123456789abcdef' for c in key_id)

def test_generate_random_password():
    # Test that password is a hex string of length 32 (16 bytes = 32 hex chars)
    password = generate_random_password()
    assert isinstance(password, str)
    assert len(password) == 32
    assert all(c in '0123456789abcdef' for c in password)

def test_create_key_with_defaults():
    # Test creating a key with only username
    username = "testuser"
    key = create_key(username)
    
    assert isinstance(key, PlainKeyContent)
    assert key.username == username
    assert key.service_name == "dorky-default"
    assert len(key.key_id) == 8
    assert len(key.password) == 32

def test_create_key_with_custom_values():
    # Test creating a key with all custom values
    username = "testuser"
    service_name = "custom-service"
    key_id = "12345678"
    password = "abcdef1234567890abcdef1234567890"
    
    key = create_key(
        username=username,
        service_name=service_name,
        key_id=key_id,
        password=password
    )
    
    assert isinstance(key, PlainKeyContent)
    assert key.username == username
    assert key.service_name == service_name
    assert key.key_id == key_id
    assert key.password == password

def test_create_key_with_partial_custom_values():
    # Test creating a key with some custom values
    username = "testuser"
    service_name = "custom-service"
    
    key = create_key(
        username=username,
        service_name=service_name
    )
    
    assert isinstance(key, PlainKeyContent)
    assert key.username == username
    assert key.service_name == service_name
    assert len(key.key_id) == 8
    assert len(key.password) == 32 