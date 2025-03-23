# MIT License
#
# Copyright (c) 2025 Clivern
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import uuid
import sqlite3
from .database import Database
from .file_system import FileSystem


class SQLite(Database):
    """
    Manages SQLite database operations,
    including backups, restores and connection testing.
    """

    def __init__(self, file_system: FileSystem, temp_path: str, db_path: str):
        """
        Initializes the SQLite instance

        Args:
            file_system (FileSystem): An instance of the FileSystem class for file operations.
            temp_path (str): The temporary directory path for storing database backups.
            db_path (str): The database path
        """
        self._file_system = file_system
        self._temp_path = temp_path.rstrip("/")
        self._db_path = db_path

    def backup(self) -> str:
        """
        Creates a backup of a SQLite database.

        Returns:
            str: the path to the backup file.
        """
        new_db_name = uuid.uuid4()
        new_db_path = f"{self._temp_path}/{new_db_name}.db"

        # Copy DB to a Temp directory
        self._file_system.copy_file(self._db_path, new_db_path)

        # Create a tar file of the db and checksum
        tar_file_path = f"{self._temp_path}/{new_db_name}.tar.gz"
        self._file_system.write_checksum_to_file(new_db_path)
        self._file_system.compress_as_tar_gz(
            new_db_path, f"{new_db_path}.checksum", tar_file_path
        )

        # Delete Temp DB paths
        self._file_system.delete_file(f"{new_db_path}.checksum")
        self._file_system.delete_file(new_db_path)

        return tar_file_path

    def restore(self, backup_path: str) -> bool:
        """
        Restore SQLite database

        Args:
            backup_path (str): The backup path

        Returns:
            bool: whether the restore succeeded or not
        """
        self._file_system.extract_tar_gz(backup_path, self._temp_path)

        file_name = os.path.basename(backup_path).replace(".tar.gz", "")
        dir_path = os.path.dirname(backup_path)

        current_db_path = f"{dir_path}/{file_name}.db"
        current_db_checksum = f"{dir_path}/{file_name}.db.checksum"

        checksum = self._file_system.read_file(current_db_checksum)

        if checksum != self._file_system.get_sha256_hash(current_db_path):
            raise Exception("Database checksum doesn't match!")

        # Restore a database file
        self._file_system.copy_file(current_db_path, self._db_path)

        # Cleanup files
        self._file_system.delete_file(current_db_checksum)
        self._file_system.delete_file(backup_path)
        self._file_system.delete_file(current_db_path)

    def connect(self) -> bool:
        """
        Tests the connection to SQLite database.

        Returns:
            bool: whether the connection succeeded or not
        """
        try:
            conn = sqlite3.connect(self._db_path)
            conn.close()
            return True
        except sqlite3.Error:
            return False


def get_sqlite(file_system: FileSystem, temp_path: str, db_path: str) -> SQLite:
    """
    Creates and returns a new SQLite instance.

    Args:
        file_system (FileSystem): An instance of the FileSystem class for file operations.
        temp_path (str): The temporary directory path for storing database backups.
        db_path (str): The SQLite database path.

    Returns:
        SQLite: A new instance of the SQLite class.
    """
    return SQLite(file_system, temp_path, db_path)
