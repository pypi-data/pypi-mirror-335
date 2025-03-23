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
import json
from typing import Any, Dict, Optional
from gulper.module import Config
from gulper.module import State
from gulper.module import Logger
from gulper.module import get_storage
from gulper.module import get_database
from gulper.module import FileSystem
from gulper.exception import BackupNotFound


class Backup:
    """
    Backup Core Functionalities
    """

    def __init__(
        self, config: Config, state: State, logger: Logger, file_system: FileSystem
    ):
        """
        Class Constructor

        Args:
            config (Config): A config instance
            state (State): A state instance
            logger (Logger): A logger instance
            file_system (FileSystem): The file system instance
        """
        self._config = config
        self._state = state
        self._logger = logger
        self._file_system = file_system

    def setup(self):
        """
        Setup calls
        """
        self._logger.get_logger().info("Connect into the state database")
        self._state.connect()
        self._logger.get_logger().info("Migrate the state database tables")
        self._state.migrate()

    def list(
        self, db_name: Optional[str], since: Optional[str]
    ) -> list[Dict[str, Any]]:
        """
        Get a list of backups

        Args:
            db_name (str): The database name
            since (str): A certain period for the backup

        Returns:
            list[Dict[str, Any]]: A list of backups
        """
        backups = self._state.get_backups(db_name, since)

        i = 0
        for backup in backups:
            backups[i]["meta"] = json.loads(backup.get("meta"))
            i += 1

        return backups

    def delete(self, id: str) -> bool:
        """
        Delete a backup by ID

        Args:
            id (str): The id of the backup

        Returns:
            bool: whether the backup is deleted or not
        """
        backup = self._state.get_backup_by_id(id)

        self._logger.get_logger().info(f"Attempt to delete a backup with id {id}")

        if backup is None:
            self._logger.get_logger().info(f"A backup with id {id} not found")
            raise BackupNotFound(f"Backup with id {id} not found!")

        meta = json.loads(backup.get("meta"))

        for file_backup in meta["backups"]:
            try:
                self._logger.get_logger().info(
                    "Delete a file {} from storage {}".format(
                        file_backup.get("file"), file_backup.get("storage_name")
                    )
                )
                storage = get_storage(self._config, file_backup.get("storage_name"))
                storage.delete_file(file_backup.get("file"))
                self._logger.get_logger().info(
                    "File {} is deleted from storage {}".format(
                        file_backup.get("file"), file_backup.get("storage_name")
                    )
                )
            except Exception as e:
                self._logger.get_logger().error(
                    "Unable to delete backup {} file {} from storage {}: {}".format(
                        id,
                        file_backup.get("file"),
                        file_backup.get("storage_name"),
                        str(e),
                    )
                )

        self._state.delete_backup(id)
        self._logger.get_logger().info(f"A backup with id {id} is deleted")
        self._state.insert_event(
            {
                "db": backup.get("db"),
                "type": "info",
                "record": f"Backup with id {id} got deleted",
            }
        )
        return True

    def get(self, id: str) -> Dict[str, Any]:
        """
        Get a backup data by ID

        Args:
            id (str): The id of the backup

        Returns:
            Dict[str, Any]: the backup data or None if backup not found
        """
        backup = self._state.get_backup_by_id(id)

        if backup is None:
            self._logger.get_logger().info(f"A backup with id {id} not found")
            raise BackupNotFound(f"Backup with id {id} not found!")

        backup["meta"] = json.loads(backup.get("meta"))

        paths = []
        backups_exists = True

        for file_backup in backup["meta"]["backups"]:
            try:
                storage = get_storage(self._config, file_backup.get("storage_name"))
                file = storage.get_file(file_backup.get("file"))
                paths.append(file.get("path"))
                self._logger.get_logger().info(
                    f"File {file_backup.get('file')} located in storage {file_backup.get('storage_name')}"
                )
            except Exception as e:
                backups_exists = False
                self._logger.get_logger().warn(
                    "Unable to locate backup {} file {} in storage {}: {}".format(
                        id,
                        file_backup.get("file"),
                        file_backup.get("storage_name"),
                        str(e),
                    )
                )

        backup["paths"] = paths
        backup["backups_exists"] = backups_exists

        return backup

    def run(self, db_name: str) -> bool:
        """
        Backup the database

        Args:
            db_name (str): The database name

        Returns:
            bool: whether backup succeeded or not
        """
        db = get_database(self._config, db_name)

        self._logger.get_logger().info(f"Backup the database with name {db_name}")

        file_path = db.backup()
        backup_id = os.path.basename(file_path).replace(".tar.gz", "")

        backups = []
        db_config = self._config.get_database_config(db_name)
        storages = db_config.get("storage", [])

        for storage_name in storages:
            storage = get_storage(self._config, storage_name)
            storage_config = self._config.get_storage_config(storage_name)

            if storage_config is None:
                self._logger.get_logger().error(
                    f"Storage {storage_name} configs are missing!"
                )
                raise Exception(f"Storage {storage_name} configs are missing!")

            remote_file_name = f"{backup_id}.tar.gz"

            try:
                self._logger.get_logger().info(
                    f"Upload file {file_path} to storage {storage_name}"
                )
                storage.upload_file(file_path, remote_file_name)
                backups.append({"storage_name": storage_name, "file": remote_file_name})
            except Exception as e:
                self._logger.get_logger().error(
                    f"Unable to upload file {file_path} to storage {storage_name}: {e}"
                )

        self._logger.get_logger().info(f"Store backup {backup_id} data")

        self._state.insert_backup(
            {
                "id": backup_id,
                "db": db_name,
                "meta": json.dumps({"backups": backups}),
                "status": "success" if len(backups) == len(storages) else "failure",
            }
        )

        if len(backups) == len(storages):
            self._state.insert_event(
                {
                    "db": db_name,
                    "type": "info",
                    "record": f"Backup with id {backup_id} succeeded",
                }
            )
        else:
            self._state.insert_event(
                {
                    "db": db_name,
                    "type": "error",
                    "record": f"Backup with id {backup_id} failed",
                }
            )

        self._file_system.delete_file(file_path)

        return True if len(backups) == len(storages) else False


def get_backup(
    config: Config, state: State, logger: Logger, file_system: FileSystem
) -> Backup:
    """
    Get Backup Class Instance

    Args:
        config (Config): A config instance
        state (State): A state instance
        logger (Logger): A logger instance

    Returns:
        Backup: An instance of backup class
    """
    return Backup(config, state, logger, file_system)
