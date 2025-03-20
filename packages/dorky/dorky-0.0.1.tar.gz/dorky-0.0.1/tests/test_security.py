import pytest
from dorky.security import (
    generate_password_hash,
    check_password_hash,
    gen_salt,
    _hash_internal,
)

def test_gen_salt():
    # Test normal case
    salt = gen_salt(16)
    assert len(salt) == 16
    assert all(c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" for c in salt)
    
    # Test minimum length
    salt = gen_salt(1)
    assert len(salt) == 1
    
    # Test invalid length
    with pytest.raises(ValueError):
        gen_salt(0)
    with pytest.raises(ValueError):
        gen_salt(-1)

def test_hash_internal():
    # Test scrypt with default parameters
    password = "test_password"
    salt = "test_salt"
    hash_val, method = _hash_internal("scrypt", salt, password)
    assert isinstance(hash_val, str)
    assert method == "scrypt:32768:8:1"
    
    # Test scrypt with custom parameters
    hash_val, method = _hash_internal("scrypt:16384:4:2", salt, password)
    assert isinstance(hash_val, str)
    assert method == "scrypt:16384:4:2"
    
    # Test pbkdf2 with default parameters
    hash_val, method = _hash_internal("pbkdf2", salt, password)
    assert isinstance(hash_val, str)
    assert method == "pbkdf2:sha256:1000000"
    
    # Test pbkdf2 with custom parameters
    hash_val, method = _hash_internal("pbkdf2:sha512:500000", salt, password)
    assert isinstance(hash_val, str)
    assert method == "pbkdf2:sha512:500000"
    
    # Test invalid method
    with pytest.raises(ValueError):
        _hash_internal("invalid_method", salt, password)

def test_generate_password_hash():
    password = "test_password"
    
    # Test default method (scrypt)
    hash_val = generate_password_hash(password)
    assert isinstance(hash_val, str)
    assert hash_val.startswith("scrypt:")
    assert len(hash_val.split("$")) == 3
    
    # Test pbkdf2 method
    hash_val = generate_password_hash(password, method="pbkdf2")
    assert isinstance(hash_val, str)
    assert hash_val.startswith("pbkdf2:")
    assert len(hash_val.split("$")) == 3
    
    # Test custom salt length
    hash_val = generate_password_hash(password, salt_length=32)
    assert isinstance(hash_val, str)
    parts = hash_val.split("$")
    assert len(parts) == 3
    assert len(parts[1]) == 32  # salt length

def test_check_password_hash():
    password = "test_password"
    
    # Test scrypt hash
    hash_val = generate_password_hash(password)
    assert check_password_hash(hash_val, password) is True
    assert check_password_hash(hash_val, "wrong_password") is False
    
    # Test pbkdf2 hash
    hash_val = generate_password_hash(password, method="pbkdf2")
    assert check_password_hash(hash_val, password) is True
    assert check_password_hash(hash_val, "wrong_password") is False
    
    # Test invalid hash format
    assert check_password_hash("invalid_hash", password) is False
    assert check_password_hash("scrypt$salt", password) is False
    assert check_password_hash("scrypt$salt$hash$extra", password) is False
    
    # Test invalid hash method
    with pytest.raises(ValueError):
        check_password_hash("invalid_method$salt$hash", password)
 