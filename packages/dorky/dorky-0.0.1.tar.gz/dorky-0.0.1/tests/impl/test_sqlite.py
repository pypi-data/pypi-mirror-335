# test dorky.impl.sqlite

import pytest
import os
import tempfile
import sqlite3
from dorky.impl.sqlite import SqliteBasedDorkyService
from dorky.types import KeyMeta, KeyWithHashedPassword, PlainKeyContent


@pytest.fixture
def temp_db_file():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        return f.name


@pytest.fixture
def sqlite_service(temp_db_file):
    return SqliteBasedDorkyService(temp_db_file)


def test_init_db(temp_db_file):
    # Test database initialization
    service = SqliteBasedDorkyService(temp_db_file)
    
    # Verify table and indexes were created
    with sqlite3.connect(temp_db_file) as conn:
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='keys'")
        assert cursor.fetchone() is not None
        
        # Check if indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        expected_indexes = {
            'idx_keys_service_name',
            'idx_keys_username',
            'idx_keys_service_username',
            'idx_keys_key_id'
        }
        assert expected_indexes.issubset(indexes)


def test_save_and_retrieve_key(sqlite_service):
    # Create a test key
    key = KeyWithHashedPassword(
        service_name="test_service",
        username="test_user",
        key_id="test_id",
        hashed_password="hashed_password"
    )

    # Save the key
    sqlite_service.save_key_to_backend(key)

    # Retrieve the key
    key_meta = KeyMeta("test_service", "test_user", "test_id")
    retrieved_key = sqlite_service.retrieve_key_from_backend(key_meta)
    assert retrieved_key is not None
    assert retrieved_key.service_name == key.service_name
    assert retrieved_key.username == key.username
    assert retrieved_key.key_id == key.key_id
    assert retrieved_key.hashed_password == key.hashed_password


def test_save_duplicate_key(sqlite_service):
    # Create a test key
    key = KeyWithHashedPassword(
        service_name="test_service",
        username="test_user",
        key_id="test_id",
        hashed_password="hash1"
    )

    # Save the key twice with different hashes
    sqlite_service.save_key_to_backend(key)
    key.hashed_password = "hash2"
    sqlite_service.save_key_to_backend(key)

    # Verify the second save overwrote the first
    key_meta = KeyMeta("test_service", "test_user", "test_id")
    retrieved_key = sqlite_service.retrieve_key_from_backend(key_meta)
    assert retrieved_key.hashed_password == "hash2"


def test_delete_key(sqlite_service):
    # Create and save a test key
    key = KeyWithHashedPassword(
        service_name="test_service",
        username="test_user",
        key_id="test_id",
        hashed_password="hashed_password"
    )
    sqlite_service.save_key_to_backend(key)

    # Delete the key
    key_meta = KeyMeta("test_service", "test_user", "test_id")
    result = sqlite_service.delete_key(key_meta)
    assert result is True

    # Verify the key was deleted
    retrieved_key = sqlite_service.retrieve_key_from_backend(key_meta)
    assert retrieved_key is None

    # Test deleting non-existent key
    result = sqlite_service.delete_key(key_meta)
    assert result is False


def test_list_keys(sqlite_service):
    # Create multiple test keys
    keys = [
        KeyWithHashedPassword("service1", "user1", "id1", "hash1"),
        KeyWithHashedPassword("service1", "user2", "id2", "hash2"),
        KeyWithHashedPassword("service2", "user1", "id3", "hash3")
    ]
    for key in keys:
        sqlite_service.save_key_to_backend(key)

    # Test listing all keys
    all_keys = sqlite_service.list_keys()
    assert len(all_keys) == 3

    # Test listing keys by service
    service1_keys = sqlite_service.list_keys(service_name="service1")
    assert len(service1_keys) == 2
    assert all(k.service_name == "service1" for k in service1_keys)

    # Test listing keys by username
    user1_keys = sqlite_service.list_keys(username="user1")
    assert len(user1_keys) == 2
    assert all(k.username == "user1" for k in user1_keys)

    # Test listing keys by both service and username
    filtered_keys = sqlite_service.list_keys(service_name="service1", username="user1")
    assert len(filtered_keys) == 1
    assert filtered_keys[0].service_name == "service1"
    assert filtered_keys[0].username == "user1"


def test_concurrent_access(temp_db_file):
    # Test concurrent access to the database
    service1 = SqliteBasedDorkyService(temp_db_file)
    service2 = SqliteBasedDorkyService(temp_db_file)

    # Create a key with service1
    key = KeyWithHashedPassword(
        service_name="test_service",
        username="test_user",
        key_id="test_id",
        hashed_password="hash1"
    )
    service1.save_key_to_backend(key)

    # Verify service2 can see the key
    key_meta = KeyMeta("test_service", "test_user", "test_id")
    retrieved_key = service2.retrieve_key_from_backend(key_meta)
    assert retrieved_key is not None
    assert retrieved_key.hashed_password == "hash1"

    # Update the key with service2
    key.hashed_password = "hash2"
    service2.save_key_to_backend(key)

    # Verify service1 sees the updated key
    retrieved_key = service1.retrieve_key_from_backend(key_meta)
    assert retrieved_key is not None
    assert retrieved_key.hashed_password == "hash2"