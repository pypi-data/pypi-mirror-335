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

from typing import Optional
from gulper.core import Backup
from gulper.module import Output


class BackupCommand:
    """
    Backup Command
    """

    def __init__(self, backup: Backup, output: Output):
        """
        Class Constructor

        Args:
            backup (Backup): backup core instance
            output (Output): output class instance
        """
        self._backup = backup
        self._output = output
        self._backup.setup()

    def list(self, db_name: Optional[str], since: Optional[str], as_json: bool):
        """
        Get a list of backups

        Args:
            db_name (Optional[str]): the database name
            since (Optional[str]): the time range
            as_json (bool): whether to output as JSON
        """
        try:
            backups = self._backup.list(db_name, since)
        except Exception as e:
            self._output.error_message(str(e), as_json)

        self._output.show_backups(backups, as_json)

    def delete(self, id: str, as_json: bool):
        """
        Delete a backup by id

        Args:
            id (str): The backup id
            as_json (bool): whether to output as JSON
        """
        try:
            result = self._backup.delete(id)
        except Exception as e:
            self._output.error_message(str(e), as_json)

        if result:
            self._output.success_message("Backup deleted successfully!", as_json)
        else:
            self._output.error_message("Backup deletion failed!", as_json)

    def get(self, id: str, as_json: bool):
        """
        Get a backup

        Args:
            id (str): The backup id
            as_json (bool): whether to output as JSON
        """
        try:
            backup = self._backup.get(id)
        except Exception as e:
            self._output.error_message(str(e), as_json)

        self._output.show_backup(backup, as_json)

    def run(self, db_name: str, as_json: bool):
        """
        Backup a database by name

        Args:
            db_name (str): The database name
            as_json (bool): whether to output as JSON
        """
        try:
            result = self._backup.run(db_name)
        except Exception as e:
            self._output.error_message(str(e), as_json)

        if result:
            self._output.success_message(
                "Database backup operation succeeded!", as_json
            )
        else:
            self._output.error_message("Database backup operation failed!", as_json)


def get_backup_command(backup: Backup, output: Output) -> BackupCommand:
    """
    Get an instance of backup command

    Args:
        backup (Backup): An instance of backup class
        output (Output): output class instance

    Returns:
        BackupCommand: an instance of backup command
    """
    return BackupCommand(backup, output)
