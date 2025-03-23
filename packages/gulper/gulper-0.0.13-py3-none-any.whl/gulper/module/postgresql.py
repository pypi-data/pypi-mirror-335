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
from typing import Optional
from .database import Database
from .file_system import FileSystem


class PostgreSQL(Database):
    """
    Manages PostgreSQL database operations,
    including backups, restores and connection testing.
    """

    def __init__(
        self,
        file_system: FileSystem,
        host: str,
        username: str,
        password: str,
        port: int,
        database: Optional[str],
        temp_path: str,
    ):
        """
        Initializes the PostgreSQL instance

        Args:
            file_system (FileSystem): The file system
            host (str): The PostgreSQL database host
            username (str): The PostgreSQL database username
            password (str): The PostgreSQL database password
            port (int): The PostgreSQL database port
            database (Optional[str]): The database to backup or None for all databases
            temp_path (str): The temp path to use for backup
        """
        self._file_system = file_system
        self._host = host
        self._username = username
        self._password = password
        self._port = port
        self._database = database
        self._temp_path = temp_path

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

        return True

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
        return f"PGPASSWORD={self._password} psql -h {self._host} -U {self._username} -p {self._port} -c 'SELECT 1'"

    def _build_dump_command(self, output_file) -> str:
        """
        Build Dump Command

        Args:
            output_file (str): The output file
        """
        if self._database:
            # For specific databases, use pg_dump
            command = f"PGPASSWORD={self._password} pg_dump -h {self._host} -U {self._username} -p {self._port} -d {self._database}"
            command += f" -c -C > {output_file}"
        else:
            # For all databases, use pg_dumpall
            command = f"PGPASSWORD={self._password} pg_dumpall -h {self._host} -U {self._username} -p {self._port}"
            command += f" -c > {output_file}"

        return command

    def _build_restore_command(self, input_file: str) -> str:
        """
        Build the psql command for restore operation.

        Args:
            input_file (str): The sql file

        Returns:
            str: the restore command
        """
        return f"PGPASSWORD={self._password} psql -h {self._host} -U {self._username} -p {self._port} -f {input_file}"

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


def get_postgresql(
    file_system: FileSystem,
    host: str,
    username: str,
    password: str,
    port: int,
    database: Optional[str],
    temp_path: str,
) -> PostgreSQL:
    """
    Get PostgreSQL instance

    Args:
        file_system (FileSystem): The file system
        host (str): The PostgreSQL database host
        username (str): The PostgreSQL database username
        password (str): The PostgreSQL database password
        port (int): The PostgreSQL database port
        database (Optiona;[str]): The database to backup or None for all databases
        temp_path (str): The temp path to use for backup

    Returns:
        PostgreSQL: The PostgreSQL instance
    """
    return PostgreSQL(file_system, host, username, password, port, database, temp_path)
