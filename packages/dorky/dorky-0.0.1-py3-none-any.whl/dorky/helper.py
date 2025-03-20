import secrets
from .types import PlainKeyContent

def generate_key_id() -> str:
    return secrets.token_hex(4)

def generate_random_password():
    return secrets.token_hex(16)

def create_key(
        username,
        service_name: str = 'dorky-default',
        key_id: str = None,
        password=None,
) -> PlainKeyContent:
    if key_id is None:
        key_id = generate_key_id()

    if password is None:
        password = generate_random_password()
    key = PlainKeyContent(service_name=service_name, username=username, key_id=key_id, password=password)
    return key

