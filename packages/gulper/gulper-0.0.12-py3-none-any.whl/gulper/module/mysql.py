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
import subprocess
from typing import Any, Dict, Optional
from .database import Database
from .file_system import FileSystem


class MySQL(Database):
    """
    Manages MySQL database operations,
    including backups, restores and connection testing.
    """

    def __init__(
        self,
        file_system: FileSystem,
        host: str,
        username: str,
        password: str,
        port: int,
        databases: list[str],
        temp_path: str,
        options: Optional[Dict[str, Any]],
    ):
        """
        Initializes the MySQL instance

        Args:
            file_system (FileSystem): The file system
            host (str): The mysql database host
            username (str): The mysql database username
            password (str): The mysql database password
            port (int): The mysql database port
            databases (list[str]): The database to backup or empty list if all databases
            temp_path (str): The temp path to use for backup
            options (Optional[Dict[str, Any]]): The list of options for backups
        """
        self._file_system = file_system
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._databases = databases
        self._temp_path = temp_path
        self._options = options

    def backup(self) -> str:
        """
        Backup the database

        Returns:
            str: the path to the backup
        """
        backup_id = str(uuid.uuid4())
        backup_sql_path = os.path.join(self._temp_path, f"{backup_id}.sql")
        backup_tar_path = os.path.join(self._temp_path, f"{backup_id}.tar.gz")

        self._file_system.write_to_file(backup_sql_path, "")

        command = self._build_dump_command(backup_sql_path)

        self._execute_command(command)

        self._file_system.write_checksum_to_file(backup_sql_path)
        self._file_system.compress_as_tar_gz(
            backup_sql_path, f"{backup_sql_path}.checksum", backup_tar_path
        )

        self._file_system.delete_file(f"{backup_sql_path}.checksum")
        self._file_system.delete_file(backup_sql_path)

        return backup_tar_path

    def restore(self, backup_path: str) -> bool:
        """
        Restore the database from a backup

        Args:
            backup_path (str): The path to .tar.gz backup

        Returns:
            bool: whether the restore succeeded or not
        """
        self._file_system.extract_tar_gz(backup_path, self._temp_path)

        file_name = os.path.basename(backup_path).replace(".tar.gz", "")
        dir_path = os.path.dirname(backup_path)

        current_db_path = f"{dir_path}/{file_name}.sql"
        current_db_checksum = f"{dir_path}/{file_name}.sql.checksum"

        checksum = self._file_system.read_file(current_db_checksum)

        if checksum != self._file_system.get_sha256_hash(current_db_path):
            raise Exception("Database checksum doesn't match!")

        # Restore a database
        restore_command = self._build_restore_command(current_db_path)
        self._execute_command(restore_command)

        # Cleanup files
        self._file_system.delete_file(current_db_checksum)
        self._file_system.delete_file(backup_path)
        self._file_system.delete_file(current_db_path)

    def connect(self) -> bool:
        """
        Connect into the database

        Returns:
            bool: whether the connection is established or not
        """
        try:
            self._execute_command(self._build_connect_command())
            return True
        except subprocess.CalledProcessError:
            return False

    def _build_connect_command(self):
        """
        Build db connect command

        Returns:
            str: The connect command
        """
        return f"mysql -h {self._host} -u {self._username} -p{self._password} -P {self._port} -e 'SELECT 1'"

    def _build_dump_command(self, output_file) -> str:
        """
        Build Dump Command

        Args:
            output_file (str): The output file
        """
        command = f"mysqldump -h {self._host} -u {self._username} -P {self._port} -p{self._password}"

        if self._databases and len(self._databases) > 0:
            dbs = " ".join(self._databases)
            command += f" --databases {dbs}"
        else:
            command += " --all-databases"

        for key, value in self._options.items():
            if isinstance(value, bool):
                if value:
                    command += f" --{key}"
            elif isinstance(value, str):
                command += f" --{key}={value}"
            elif isinstance(value, list):
                for item in value:
                    command += f" --{key}={item}"

        command += f" > {output_file}"

        return command

    def _build_restore_command(self, input_file: str) -> str:
        """
        Build the mysql command for restore operation.

        Args:
            input_file (str): The sql file

        Returns:
            str: the restore command
        """
        return f"mysql -h {self._host} -u {self._username} -p{self._password} -P {self._port} < {input_file}"

    def _execute_command(self, command: str) -> None:
        """
        Execute a shell command.

        Args:
            command (str): Command string to execute
        """
        process = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if process.returncode != 0:
            raise Exception(f"Error: {process.stderr.decode()}")


def get_mysql(
    file_system: FileSystem,
    host: str,
    username: str,
    password: str,
    port: int,
    databases: list[str],
    temp_path: str,
    options: Optional[Dict[str, Any]],
) -> MySQL:
    """
    Get MySQL instance

    Args:
        file_system (FileSystem): The file system
        host (str): The mysql database host
        username (str): The mysql database username
        password (str): The mysql database password
        port (int): The mysql database port
        databases (list[str]): The database to backup or empty list if all databases
        temp_path (str): The temp path to use for backup
        options (Optional[Dict[str, Any]]): The list of options for backups

    Returns:
        MySQL: The mysql instance
    """
    return MySQL(
        file_system, host, username, password, port, databases, temp_path, options
    )
