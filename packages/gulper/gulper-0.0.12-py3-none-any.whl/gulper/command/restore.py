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
from gulper.core import Restore
from gulper.module import Output


class RestoreCommand:
    """
    Restore Command
    """

    def __init__(self, restore: Restore, output: Output):
        """
        Class Constructor

        Args:
            restore (Restore): The restore class instance
            output (Output): output class instance
        """
        self._restore = restore
        self._output = output
        self._restore.setup()

    def run(self, db_name: Optional[str], backup_id: Optional[str], as_json: bool):
        """
        Restore the database

        Args:
            db_name (str): The database name
            backup_id (str): The backup id
            as_json (bool): Whether to return output as JSON
        """
        try:
            result = self._restore.run(db_name, backup_id)
        except Exception as e:
            self._output.error_message(str(e), as_json)

        if result:
            self._output.success_message(
                "Database restore operation succeeded!", as_json
            )
        else:
            self._output.error_message("Database restore operation failed!", as_json)


def get_restore_command(restore: Restore, output: Output) -> RestoreCommand:
    """
    Get an instance of restore command

    Args:
        restore (Restore): An instance of restore class
        output (Output): output class instance

    Returns:
        RestoreCommand: an instance of restore command
    """
    return RestoreCommand(restore, output)
