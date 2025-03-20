# test dorky.service

import pytest
from unittest.mock import MagicMock, patch
from dorky.service import BaseDorkyService
from dorky.types import KeyMeta, PlainKeyContent, KeyWithHashedPassword


class MockDorkyService(BaseDorkyService):
    def __init__(self):
        super().__init__()
        self._keys = {}

    def save_key_to_backend(self, key: KeyWithHashedPassword):
        self._keys[key.key_id] = key

    def retrieve_key_from_backend(self, key_meta: KeyMeta) -> KeyWithHashedPassword:
        return self._keys.get(key_meta.key_id)

    def delete_key(self, key_meta: KeyMeta) -> bool:
        if key_meta.key_id in self._keys:
            del self._keys[key_meta.key_id]
            return True
        return False

    def list_keys(self, service_name=None, username=None):
        keys = []
        for key in self._keys.values():
            if (service_name is None or key.service_name == service_name) and \
               (username is None or key.username == username):
                keys.append(KeyMeta(key.service_name, key.username, key.key_id))
        return keys


@pytest.fixture
def mock_service():
    return MockDorkyService()


def test_create_key(mock_service):
    # Test creating a key with default service name
    key = mock_service.create_key("testuser")
    assert key.username == "testuser"
    assert key.service_name == "dorky-default"
    assert key.key_id is not None
    assert key.password is not None

    # Test creating a key with custom service name and key_id
    key = mock_service.create_key("testuser", service_name="custom-service", key_id="test-id")
    assert key.username == "testuser"
    assert key.service_name == "custom-service"
    assert key.key_id == "test-id"
    assert key.password is not None


def test_verify_key(mock_service):
    # Create and save a key
    key = mock_service.create_key("testuser", service_name="test-service")
    
    # Test verification with correct key
    assert mock_service.verify_key(key) is True
    
    # Test verification with incorrect password
    wrong_key = PlainKeyContent(key.service_name, key.username, key.key_id, "wrong-password")
    assert mock_service.verify_key(wrong_key) is False
    
    # Test verification with non-existent key
    non_existent_key = PlainKeyContent("non-existent", "testuser", "non-existent-id", "password")
    assert mock_service.verify_key(non_existent_key) is False


def test_verify_key_str(mock_service):
    # Create and save a key
    key = mock_service.create_key("testuser", service_name="test-service")
    
    # Test verification with correct key string
    assert mock_service.verify_key_str(key.encode()) is True
    
    # Test verification with incorrect key string
    wrong_key_str = f"{key.service_name}:{key.username}:{key.key_id}:wrong-password"
    assert mock_service.verify_key_str(wrong_key_str) is False
    
    # Test verification with invalid key string format
    with pytest.raises(ValueError):
        mock_service.verify_key_str("invalid:format")


def test_verify_key_with_return(mock_service):
    # Create and save a key
    key = mock_service.create_key("testuser", service_name="test-service")
    
    # Test verification with return_key=True
    result, returned_key = mock_service.verify_key(key, return_key=True)
    assert result is True
    assert returned_key == key
    
    # Test verification with incorrect key and return_key=True
    wrong_key = PlainKeyContent(key.service_name, key.username, key.key_id, "wrong-password")
    result, returned_key = mock_service.verify_key(wrong_key, return_key=True)
    assert result is False
    assert returned_key == wrong_key


def test_list_keys(mock_service):
    # Create multiple keys
    mock_service.create_key("user1", service_name="service1")
    mock_service.create_key("user1", service_name="service2")
    mock_service.create_key("user2", service_name="service1")
    
    # Test listing all keys
    all_keys = mock_service.list_keys()
    assert len(all_keys) == 3
    
    # Test listing keys by service
    service1_keys = mock_service.list_keys(service_name="service1")
    assert len(service1_keys) == 2
    
    # Test listing keys by username
    user1_keys = mock_service.list_keys(username="user1")
    assert len(user1_keys) == 2
    
    # Test listing keys by both service and username
    filtered_keys = mock_service.list_keys(service_name="service1", username="user1")
    assert len(filtered_keys) == 1


def test_delete_key(mock_service):
    # Create and save a key
    key = mock_service.create_key("testuser", service_name="test-service")
    
    # Test deleting existing key
    assert mock_service.delete_key(key) is True
    assert mock_service.retrieve_key_from_backend(key) is None
    
    # Test deleting non-existent key
    non_existent_key = KeyMeta("non-existent", "testuser", "non-existent-id")
    assert mock_service.delete_key(non_existent_key) is False