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

from .database import Database
from .sqlite import get_sqlite
from .mysql import get_mysql
from .config import Config
from .file_system import get_file_system


def get_database(config: Config, db_name: str) -> Database:
    db_config = config.get_database_config(db_name)

    if db_config is None:
        raise Exception(f"Database {db_name} not found")

    if db_config.get("type") == "sqlite":
        return get_sqlite(
            get_file_system(), config.get_temp_dir(), db_config.get("path")
        )
    elif db_config.get("type") == "mysql":
        return get_mysql(
            get_file_system(),
            db_config.get("host"),
            db_config.get("username"),
            db_config.get("password"),
            db_config.get("port", 3306),
            db_config.get("database", []),
            config.get_temp_dir(),
            db_config.get("options", {}),
        )
