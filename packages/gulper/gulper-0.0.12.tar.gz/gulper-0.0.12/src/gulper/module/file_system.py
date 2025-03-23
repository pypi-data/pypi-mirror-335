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
import shutil
import tarfile
import hashlib
from typing import Any, Dict
from datetime import datetime


class FileSystem:
    """FileSystem Utils Class"""

    def compress_as_tar_gz(self, input_file: str, checksum_file: str, output_file: str):
        """
        Compresses a file into a tar.gz archive.

        Args:
            input_file (str): The path to the file to be compressed.
            checksum_file (str): The path to input file checksum file
            output_file (str): The path where the compressed tar.gz file will be saved.

        Returns:
            None
        """
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(input_file, arcname=os.path.basename(input_file))
            tar.add(checksum_file, arcname=os.path.basename(checksum_file))

    def extract_tar_gz(self, tar_file_path: str, extract_to: str):
        """
        Extracts the contents of a tar.gz file to a specified directory.

        Args:
            tar_file_path (str): The path to the tar.gz file to be extracted.
            extract_to (str): The directory where the contents will be extracted.

        Returns:
            None
        """
        with tarfile.open(tar_file_path, "r:gz") as tar:
            tar.extractall(extract_to)

    def copy_file(self, from_path: str, to_path: str) -> bool:
        """
        Backup a file.

        Args:
            from_path (str): The path to the source file.
            to_path (str): The path where the backup will be saved.

        Returns:
            bool: True if the backup was successful, False otherwise.

        Raises:
            FileNotFoundError: If the source file doesn't exist.
            IOError: If the backup file couldn't be created.
        """
        # Ensure the source file exists
        if not os.path.exists(from_path):
            raise FileNotFoundError(f"Source file not found: {from_path}")

        # Copy the file
        shutil.copy2(from_path, to_path)

        # Verify the backup
        if not os.path.exists(to_path):
            raise IOError("Backup file was not created successfully")

        return True

    def rename_file(self, old_name: str, new_name: str) -> bool:
        """
        Renames a file.

        Args:
            old_name (str): The current path and name of the file.
            new_name (str): The new path and name for the file.

        Returns:
            bool: True if the file was successfully renamed, False otherwise.

        Raises:
            FileNotFoundError: If the source file doesn't exist.
            FileExistsError: If a file with the new name already exists.
        """
        # Check if the source file exists
        if not os.path.exists(old_name):
            raise FileNotFoundError(f"Source file not found: {old_name}")

        # Check if a file with the new name already exists
        if os.path.exists(new_name):
            raise FileExistsError(f"A file with the name {new_name} already exists")

        os.rename(old_name, new_name)

        return True

    def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file.

        Args:
            file_path (str): The path to the file to be deleted.

        Returns:
            bool: True if the file was successfully deleted, False otherwise.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            PermissionError: If permission is denied to delete the file.
            OSError: If an OS-related error occurs during deletion.
        """
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            os.remove(file_path)
            return True
        except PermissionError:
            raise PermissionError(f"Permission denied to delete file: {file_path}")
        except OSError as e:
            raise OSError(f"An error occurred while deleting the file: {e}")

    def read_file(self, path: str) -> str:
        """
        Reads the entire content of a file and returns it as a string.

        Args:
            path (str): The path to the file to be read.

        Returns:
            str: The entire content of the file as a string.
        """
        with open(path, "r") as file:
            return file.read()

    def write_checksum_to_file(self, file_path: str) -> str:
        """
        Calculates the SHA256 checksum of a file and writes it to a text file with the .checksum extension.

        Args:
            file_path (str): The path to the file for which the checksum will be generated.

        Returns:
            str: The path to the checksum file.
        """
        checksum = self.get_sha256_hash(file_path)

        # Create the checksum file path
        checksum_file_path = f"{file_path}.checksum"

        # Write the checksum to the file
        with open(checksum_file_path, "w") as f:
            f.write(checksum)

        return checksum_file_path

    def get_sha256_hash(self, file_path: str) -> str:
        """
        Calculates the SHA256 hash of a file.

        Args:
            file_path (str): The path to the file for which the SHA256 hash will be calculated.

        Returns:
            str: The SHA256 hash of the file.
        """
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        return sha256_hash.hexdigest()

    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """
        Get File Stats

        Args:
            file_path (str): The file path

        Returns:
            The file stats
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        file_stats = os.stat(file_path)

        return {
            "path": file_path,
            "size": file_stats.st_size,
            "mod_time": datetime.fromtimestamp(file_stats.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    def write_to_file(self, path, content) -> bool:
        """
        Write to a file

        Args:
            path: The file path
            content: The file content

        Returns:
            bool: whether the operation succeeded or not
        """
        with open(path, "w") as file:
            file.write(content)
        return True


def get_file_system() -> FileSystem:
    return FileSystem()
