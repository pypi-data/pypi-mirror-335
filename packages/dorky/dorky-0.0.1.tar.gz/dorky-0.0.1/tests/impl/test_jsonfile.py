# test dorky.impl.jsonfile

import pytest
import os
import json
import tempfile
from dorky.impl.jsonfile import JsonBasedDorkyService
from dorky.types import KeyMeta, KeyWithHashedPassword, PlainKeyContent


@pytest.fixture
def temp_json_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"keys": []}, f)
        return f.name


@pytest.fixture
def json_service(temp_json_file):
    return JsonBasedDorkyService(temp_json_file)


def test_init_with_existing_file(temp_json_file):
    # Test initialization with existing file
    service = JsonBasedDorkyService(temp_json_file)
    assert service.data == {"keys": []}

    # Test initialization with non-existent file without overwrite
    with pytest.raises(Exception):
        JsonBasedDorkyService("non_existent.json")

    # Test initialization with non-existent file with overwrite
    service = JsonBasedDorkyService("new_file.json", overwrite=True)
    assert service.data == {"keys": []}
    os.remove("new_file.json")


def test_save_and_retrieve_key(json_service, temp_json_file):
    # Create a test key
    key = KeyWithHashedPassword(
        service_name="test_service",
        username="test_user",
        key_id="test_id",
        hashed_password="hashed_password"
    )

    # Save the key
    json_service.save_key_to_backend(key)

    # Verify the key was saved to the file
    with open(temp_json_file, 'r') as f:
        data = json.load(f)
        assert len(data["keys"]) == 1
        assert data["keys"][0]["service_name"] == "test_service"
        assert data["keys"][0]["username"] == "test_user"
        assert data["keys"][0]["key_id"] == "test_id"
        assert data["keys"][0]["hashed_password"] == "hashed_password"

    # Retrieve the key
    key_meta = KeyMeta("test_service", "test_user", "test_id")
    retrieved_key = json_service.retrieve_key_from_backend(key_meta)
    assert retrieved_key is not None
    assert retrieved_key.service_name == key.service_name
    assert retrieved_key.username == key.username
    assert retrieved_key.key_id == key.key_id
    assert retrieved_key.hashed_password == key.hashed_password


def test_delete_key(json_service):
    # Create and save a test key
    key = KeyWithHashedPassword(
        service_name="test_service",
        username="test_user",
        key_id="test_id",
        hashed_password="hashed_password"
    )
    json_service.save_key_to_backend(key)

    # Delete the key
    key_meta = KeyMeta("test_service", "test_user", "test_id")
    json_service.delete_key(key_meta)

    # Verify the key was deleted
    retrieved_key = json_service.retrieve_key_from_backend(key_meta)
    assert retrieved_key is None


def test_list_keys(json_service):
    # Create multiple test keys
    keys = [
        KeyWithHashedPassword("service1", "user1", "id1", "hash1"),
        KeyWithHashedPassword("service1", "user2", "id2", "hash2"),
        KeyWithHashedPassword("service2", "user1", "id3", "hash3")
    ]
    for key in keys:
        json_service.save_key_to_backend(key)

    # Test listing all keys
    all_keys = json_service.list_keys()
    assert len(all_keys) == 3

    # Test listing keys by service
    service1_keys = json_service.list_keys(service_name="service1")
    assert len(service1_keys) == 2
    assert all(k.service_name == "service1" for k in service1_keys)

    # Test listing keys by username
    user1_keys = json_service.list_keys(username="user1")
    assert len(user1_keys) == 2
    assert all(k.username == "user1" for k in user1_keys)

    # Test listing keys by both service and username
    filtered_keys = json_service.list_keys(service_name="service1", username="user1")
    assert len(filtered_keys) == 1
    assert filtered_keys[0].service_name == "service1"
    assert filtered_keys[0].username == "user1"


def test_corrupted_json_file():
    # Create a corrupted JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json content")
        temp_file = f.name

    # Test initialization with corrupted file
    with pytest.raises(Exception):
        JsonBasedDorkyService(temp_file)

    os.remove(temp_file)