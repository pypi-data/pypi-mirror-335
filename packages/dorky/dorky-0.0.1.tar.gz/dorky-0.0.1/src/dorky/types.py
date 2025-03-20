from .security import generate_password_hash


class KeyMeta:
    key_id: str
    username: str
    service_name: str

    def __init__(self, service_name: str, username: str, key_id: str):
        self.key_id = key_id
        self.username = username
        self.service_name = service_name

    def get_key_id(self):
        return self.key_id

    def get_username(self):
        return self.username

    def get_service_name(self):
        return self.service_name


class PlainKeyContent(KeyMeta):
    password: str

    def __init__(self, service_name: str, username: str, key_id: str, password: str):
        super().__init__(service_name, username, key_id)
        self.password = password

    def encode(self):
        return f"{self.service_name}:{self.username}:{self.key_id}:{self.password}"

    def to_dict(self):
        return {
            "service_name": self.service_name,
            "username": self.username,
            "key_id": self.key_id,
            "password": self.password
        }

    @staticmethod
    def decode_key_str(content: str):
        service_name, username, key_id, password = content.split(":")
        return PlainKeyContent(service_name, username, key_id, password)

    def hash_password(self) -> 'KeyWithHashedPassword':
        hashed_password = generate_password_hash(self.password)
        return KeyWithHashedPassword(self.service_name, self.username, self.key_id, hashed_password)

class KeyWithHashedPassword(KeyMeta):
    hashed_password: str

    def __init__(self, service_name: str, username: str, key_id: str, hashed_password: str):
        super().__init__(service_name, username, key_id)
        self.hashed_password = hashed_password

    def to_dict(self):
        return {
            "service_name": self.service_name,
            "username": self.username,
            "key_id": self.key_id,
            "hashed_password": self.hashed_password
        }
