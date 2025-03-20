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
import boto3
from .config import Config
from abc import ABC, abstractmethod
from .file_system import FileSystem
from typing import Dict, Any, Optional
from botocore.client import BaseClient as Boto3Client


class Storage(ABC):
    """
    Storage Class
    """

    @abstractmethod
    def upload_file(self, local_file_path: str, remote_file_name: str) -> bool:
        """
        Download a file from remote storage whether it is a local or S3 to
        a local path

        Args:
            local_file_path (str): The local file path
            remote_file_name (str): The remote file name

        Returns:
            Whether upload succeeded or not
        """
        pass

    @abstractmethod
    def download_file(self, remote_file_name: str, local_path: str) -> bool:
        """
        Download a file from remote storage whether it is a local or S3 to
        a local path

        Args:
            remote_file_path (str): The remote file name
            local_path (str): The location to download into

        Returns:
            Whether download succeeded or not
        """
        pass

    @abstractmethod
    def delete_file(self, remote_file_name: str) -> bool:
        """
        Delete a file from remote storage whether it is a local or S3

        Args:
            remote_file_name (str): The remote file name

        Returns:
            Whether the file is deleted or not
        """
        pass

    @abstractmethod
    def get_file(self, remote_file_name: str) -> Dict[str, Any]:
        """
        Get a file from remote storage whether it is a local or S3

        Args:
            remote_file_name (str): The remote file name

        Returns:
            The file data
        """
        pass

    @abstractmethod
    def get_files(self) -> list[Dict[str, Any]]:
        """
        Get file list from remote storage whether it is a local or S3

        Returns:
            The files data
        """
        pass

    @abstractmethod
    def get_base_path(self) -> str:
        """
        Get storage base path whether a local or remote S3

        Returns:
            The storage base path
        """
        pass


class LocalStorage(Storage):
    """
    Storage Class
    """

    def __init__(self, file_system: FileSystem, base_path: str):
        """
        Class Constructor
        """
        self._base_path = base_path
        self._file_system = file_system

    def upload_file(self, local_file_path: str, remote_file_name: str) -> bool:
        """
        Upload a file to a remote local storage

        Args:
            local_file_path (str): The local file path
            remote_file_name (str): The remote file name

        Returns:
            Whether upload succeeded or not
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name)
        return self._file_system.copy_file(local_file_path, remote_file_path)

    def download_file(self, remote_file_name: str, local_path: str) -> bool:
        """
        Download a file from a remote local storage

        Args:
            remote_file_path (str): The remote file name
            local_path (str): The location to download into

        Returns:
            Whether download succeeded or not
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name)
        return self._file_system.copy_file(remote_file_path, local_path)

    def delete_file(self, remote_file_name: str) -> bool:
        """
        Delete a file from a remote local storage

        Args:
            remote_file_name (str): The remote file name

        Returns:
            Whether the file is deleted or not
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name)
        return self._file_system.delete_file(remote_file_path)

    def get_file(self, remote_file_name: str) -> Dict[str, Any]:
        """
        Get a file from remote local storage

        Args:
            remote_file_name (str): The remote file name

        Returns:
            The file data
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name)
        return self._file_system.get_file_stats(remote_file_path)

    def get_files(self) -> list[Dict[str, Any]]:
        """
        Get file list from remote local storage

        Returns:
            The files data
        """
        files_data = []

        for filename in os.listdir(self.get_base_path()):
            remote_file_path = os.path.join(self.get_base_path(), filename)

            if os.path.isfile(remote_file_path):
                files_data.append(self._file_system.get_file_stats(remote_file_path))

        return files_data

    def get_base_path(self) -> str:
        """
        Get local storage base path

        Returns:
            The storage base path
        """
        return self._base_path


class S3Storage(Storage):
    """S3 Backed Storage Class"""

    def __init__(
        self,
        boto3_client: Boto3Client,
        bucket_name: str,
        base_path: str,
    ):
        """
        Class Constructor
        """
        self._boto3_client = boto3_client
        self._bucket_name = bucket_name
        self._base_path = base_path

    def upload_file(self, local_file_path: str, remote_file_name: str) -> bool:
        """
        Upload a file to a remote S3 storage

        Args:
            local_file_path (str): The local file path
            remote_file_name (str): The remote file name

        Returns:
            Whether upload succeeded or not
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name).lstrip(
            "/"
        )
        self._boto3_client.upload_file(
            local_file_path, self._bucket_name, remote_file_path
        )
        return True

    def download_file(self, remote_file_name: str, local_path: str) -> bool:
        """
        Download a file from a remote S3 storage

        Args:
            remote_file_path (str): The remote file name
            local_path (str): The location to download into

        Returns:
            Whether download succeeded or not
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name).lstrip(
            "/"
        )
        self._boto3_client.download_file(
            self._bucket_name, remote_file_path, local_path
        )
        return True

    def delete_file(self, remote_file_name: str) -> bool:
        """
        Delete a file from remote S3 storage

        Args:
            remote_file_name (str): The remote file name

        Returns:
            Whether the file is deleted or not
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name).lstrip(
            "/"
        )
        self._boto3_client.delete_object(Bucket=self._bucket_name, Key=remote_file_path)
        return True

    def get_file(self, remote_file_name: str) -> Dict[str, Any]:
        """
        Get a file from remote local storage

        Args:
            remote_file_name (str): The remote file name

        Returns:
            The file data
        """
        remote_file_path = os.path.join(self.get_base_path(), remote_file_name).lstrip(
            "/"
        )

        response = self._boto3_client.head_object(
            Bucket=self._bucket_name, Key=remote_file_path
        )

        return {
            "path": f"s3://{self._bucket_name}/{remote_file_path}",
            "size": response["ContentLength"],
            "mod_time": response["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
        }

    def get_files(self) -> list[Dict[str, Any]]:
        """
        Get file list from remote local storage

        Returns:
            The files data
        """
        files_data = []
        response = self._boto3_client.list_objects_v2(
            Bucket=self._bucket_name, Prefix=self._base_path.lstrip("/")
        )

        for obj in response.get("Contents", []):
            if obj["Key"].startswith(self._base_path.lstrip("/")) and not obj[
                "Key"
            ].endswith("/"):
                file_data = {
                    "path": f"s3://{self._bucket_name}/{obj['Key']}",
                    "size": obj["Size"],
                    "mod_time": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
                }
                files_data.append(file_data)

        return files_data

    def get_base_path(self) -> str:
        """
        Get S3 storage base path

        Returns:
            The storage base path
        """
        return self._base_path


def get_local_storage(file_system: FileSystem, base_path: str) -> LocalStorage:
    return LocalStorage(file_system, base_path)


def get_s3_storage(
    boto3_client: Boto3Client, bucket_name: str, base_path: str
) -> S3Storage:
    return S3Storage(boto3_client, bucket_name, base_path)


def get_boto3_client(
    access_key_id: str, secret_access_key: str, region_name, endpoint_url: Optional[str]
) -> Boto3Client:
    """
    Get Boto3 Client

    Args:
        access_key_id (str): The access key id
        secret_access_key (str): The secret access key

    Returns:
        The Boto3 Client
    """
    if not endpoint_url:
        return boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )
    else:
        return boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url,
        )


def get_storage(config: Config, storage_name: str) -> Storage:
    storage = config.get_storage_config(storage_name)

    if storage is None:
        raise Exception(f"Storage with name {storage_name} is not found!")

    if storage.get("type") == "local":
        return get_local_storage(FileSystem(), storage.get("path"))
    elif storage.get("type") == "s3":
        return get_s3_storage(
            get_boto3_client(
                storage.get("access_key_id"),
                storage.get("secret_access_key"),
                storage.get("region"),
                storage.get("endpoint_url", None),
            ),
            storage.get("bucket_name"),
            storage.get("path"),
        )
