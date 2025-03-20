import os

from json import JSONDecodeError

import json

from typing import Optional, TypedDict

from dorky import KeyMeta, KeyWithHashedPassword, PlainKeyContent
from dorky.service import BaseDorkyService


class KeyInfo(TypedDict):
    service_name: str
    username: str
    key_id: str
    hashed_password: str


class UsersDict(TypedDict):
    keys: list[KeyInfo]


def try_load_json_user_dict(file_location) -> Optional[UsersDict]:
    try:
        if os.path.exists(file_location) is False:
            return None

        with open(file_location, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                if "keys" in data:
                    if isinstance(data["keys"], list):
                        return data
    except JSONDecodeError:
        return None


class JsonBasedDorkyService(BaseDorkyService):

    def __init__(self, file_location, overwrite=False):
        super().__init__()
        self.file_location = file_location
        self.data = try_load_json_user_dict(file_location)
        if self.data is None:
            if overwrite is False:
                raise Exception(f"Could not load existing file at {file_location}")
            else:
                self.data = {"keys": []}
                self.write_json()

    def write_json(self):
        with open(self.file_location, 'w') as f:
            json.dump(self.data, f)

    def save_key_to_backend(self, key: KeyWithHashedPassword):
        self.data["keys"].append({
            "service_name": key.service_name,
            "username": key.username,
            "key_id": key.key_id,
            "hashed_password": key.hashed_password
        })
        self.write_json()

    def retrieve_key_from_backend(self, key_meta: KeyMeta) -> Optional[KeyWithHashedPassword]:
        for key_info in self.data["keys"]:
            if key_info["service_name"] == key_meta.get_service_name() and \
                    key_info["username"] == key_meta.get_username() and \
                    key_info["key_id"] == key_meta.get_key_id():
                return KeyWithHashedPassword(
                    key_info["service_name"],
                    key_info["username"],
                    key_info["key_id"],
                    key_info["hashed_password"]
                )
        return None

    def delete_key(self, key_meta: KeyMeta):
        for key_info in self.data["keys"]:
            if key_info["service_name"] == key_meta.get_service_name() and \
                    key_info["username"] == key_meta.get_username() and \
                    key_info["key_id"] == key_meta.get_key_id():
                self.data["keys"].remove(key_info)
                self.write_json()
                
    def list_keys(self, service_name: Optional[str] = None, username: Optional[str] = None):
        """List all keys, optionally filtered by service_name and/or username."""
        if not self.data or "keys" not in self.data:
            return []
            
        filtered_keys = self.data["keys"]
        
        if service_name:
            filtered_keys = [k for k in filtered_keys if k["service_name"] == service_name]
            
        if username:
            filtered_keys = [k for k in filtered_keys if k["username"] == username]
            
        return [
            KeyMeta(
                service_name=k["service_name"],
                username=k["username"],
                key_id=k["key_id"],
            )
            for k in filtered_keys
        ]