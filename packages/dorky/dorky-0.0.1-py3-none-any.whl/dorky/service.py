import abc
import typing
from typing import Optional

from .types import KeyWithHashedPassword, PlainKeyContent, KeyMeta
from .security import check_password_hash, generate_password_hash
from .helper import create_key


class BaseDorkyService:
    def __init__(self):
        pass

    @abc.abstractmethod
    def save_key_to_backend(self, key: KeyWithHashedPassword):
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_key_from_backend(self, key_meta: KeyMeta) -> Optional[KeyWithHashedPassword]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete_key(self, key_meta: KeyMeta) -> bool:
        raise NotImplementedError
    
    @abc.abstractmethod
    def list_keys(self, service_name: Optional[str] = None, username: Optional[str] = None) -> list[KeyMeta]:
        raise NotImplementedError


    def create_key(self, username, service_name='dorky-default', key_id=None):
        """
        Creates and saves a service key for the specified username and service name.

        This method generates a service key for the provided username and an optional
        service name and key ID. The generated key is then saved to the backend storage
        through a corresponding method.

        Args:
            username (str): The username for which the key is generated.
            service_name (str, optional): The name of the service associated with the key,
                defaults to 'dorky-default'.
            key_id (str, optional): The identifier for the key. If None, an auto-generated
                identifier will be used.

        Returns:
            The created key object after saving to the backend.
        """
        key = create_key(username, key_id=key_id, service_name=service_name)
        self.save_key_to_backend(key.hash_password())
        return key

    def verify_key_str(self, key_str: str, return_key=False) -> typing.Union[bool, tuple[bool, PlainKeyContent]]:
        """
        Verifies the provided key string by decoding it and checking its validity.

        This function decodes a given key string using the `PlainKeyContent` class and verifies its
        contents. The method can also optionally return the decoded key data alongside the verification
        result if requested.

        Parameters
        ----------
        key_str : str
            The string representation of a key that needs to be verified.
        return_key : bool, default=False
            Determines whether to return the decoded key along with the verification result.

        Returns
        -------
        Union[bool, tuple[bool, PlainKeyContent]]
            If `return_key` is False, returns a boolean indicating whether the key is valid. If `return_key`
            is True, returns a tuple containing the validity result (boolean) and the decoded key data
            (PlainKeyContent instance).
        """
        key = PlainKeyContent.decode_key_str(key_str)
        return self.verify_key(key, return_key=return_key)

    def verify_key(self, key: PlainKeyContent, return_key=False) -> typing.Union[bool, tuple[bool, PlainKeyContent]]:
        """
        Verifies the provided key against a stored key's hashed password. This function checks
        if the provided key matches the stored hashed password retrieved from the backend. If
        `return_key` is set to True, it returns a tuple containing the verification status and
        the provided key; otherwise, it returns only the verification status as a boolean. If
        no stored key is found, the function returns False.

        Parameters:
            key (PlainKeyContent): The key object that contains the password to be verified.
            return_key (bool): Optional flag indicating whether to return the key object along
                with the verification result.

        Returns:
            typing.Union[bool, tuple[bool, PlainKeyContent]]: If `return_key` is False, returns
            a boolean indicating whether the key matches the stored hashed password. If
            `return_key` is True, returns a tuple where the first element is the boolean
            verification result, and the second element is the provided key.

        Raises:
            None: This function does not raise exceptions.
        """
        saved_key = self.retrieve_key_from_backend(key)
        if saved_key:
            if return_key:
                return check_password_hash(saved_key.hashed_password, key.password), key
            else:
                return check_password_hash(saved_key.hashed_password, key.password)
        return False
