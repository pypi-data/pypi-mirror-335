import sqlite3
from typing import Optional
import os

from dorky import KeyMeta, KeyWithHashedPassword
from dorky.service import BaseDorkyService


class SqliteBasedDorkyService(BaseDorkyService):
    def __init__(self, file_location):
        super().__init__()
        self.file_location = file_location
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database and create the keys table and indexes if they don't exist."""
        with sqlite3.connect(self.file_location) as conn:
            cursor = conn.cursor()
            
            # Create the main table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS keys (
                    service_name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    key_id TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    PRIMARY KEY (service_name, username, key_id)
                )
            ''')
            
            # Create indexes for common query patterns
            # Index for service_name lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_keys_service_name 
                ON keys(service_name)
            ''')
            
            # Index for username lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_keys_username 
                ON keys(username)
            ''')
            
            # Composite index for service_name + username lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_keys_service_username 
                ON keys(service_name, username)
            ''')
            
            # Index for key_id lookups (though less common, might be useful)
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_keys_key_id 
                ON keys(key_id)
            ''')
            
            conn.commit()

    def save_key_to_backend(self, key: KeyWithHashedPassword):
        """Save a key to the SQLite database."""
        with sqlite3.connect(self.file_location) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO keys (service_name, username, key_id, hashed_password)
                VALUES (?, ?, ?, ?)
            ''', (
                key.service_name,
                key.username,
                key.key_id,
                key.hashed_password
            ))
            conn.commit()

    def retrieve_key_from_backend(self, key_meta: KeyMeta) -> Optional[KeyWithHashedPassword]:
        """Retrieve a key from the SQLite database."""
        with sqlite3.connect(self.file_location) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT service_name, username, key_id, hashed_password
                FROM keys
                WHERE service_name = ? AND username = ? AND key_id = ?
            ''', (
                key_meta.get_service_name(),
                key_meta.get_username(),
                key_meta.get_key_id()
            ))
            row = cursor.fetchone()
            
            if row:
                return KeyWithHashedPassword(
                    service_name=row[0],
                    username=row[1],
                    key_id=row[2],
                    hashed_password=row[3]
                )
            return None

    def delete_key(self, key_meta: KeyMeta) -> bool:
        """Delete a key from the SQLite database."""
        with sqlite3.connect(self.file_location) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM keys
                WHERE service_name = ? AND username = ? AND key_id = ?
            ''', (
                key_meta.get_service_name(),
                key_meta.get_username(),
                key_meta.get_key_id()
            ))
            conn.commit()
            return cursor.rowcount > 0

    def list_keys(self, service_name: Optional[str] = None, username: Optional[str] = None) -> list[KeyWithHashedPassword]:
        """List all keys, optionally filtered by service_name and/or username."""
        with sqlite3.connect(self.file_location) as conn:
            cursor = conn.cursor()
            
            if service_name and username:
                cursor.execute('''
                    SELECT service_name, username, key_id, hashed_password
                    FROM keys
                    WHERE service_name = ? AND username = ?
                ''', (service_name, username))
            elif service_name:
                cursor.execute('''
                    SELECT service_name, username, key_id, hashed_password
                    FROM keys
                    WHERE service_name = ?
                ''', (service_name,))
            elif username:
                cursor.execute('''
                    SELECT service_name, username, key_id, hashed_password
                    FROM keys
                    WHERE username = ?
                ''', (username,))
            else:
                cursor.execute('''
                    SELECT service_name, username, key_id, hashed_password
                    FROM keys
                ''')
            
            return [
                KeyWithHashedPassword(
                    service_name=row[0],
                    username=row[1],
                    key_id=row[2],
                    hashed_password=row[3]
                )
                for row in cursor.fetchall()
            ]
