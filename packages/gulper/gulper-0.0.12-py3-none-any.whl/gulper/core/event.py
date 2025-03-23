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

from gulper.module import Config
from gulper.module import State
from gulper.module import Logger
from typing import Any, Dict, Optional


class Event:
    """
    Event Core Functionalities
    """

    def __init__(self, config: Config, state: State, logger: Logger):
        """
        Class Constructor

        Args:
            config (Config): A config instance
            state (State): A state instance
            logger (Logger): A logger instance
        """
        self._config = config
        self._state = state
        self._logger = logger

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
        Get a list of events

        Args:
            db_name (str): The database name
            since (str): A certain period for the backup

        Returns:
            list[Dict[str, Any]]: A list of events
        """
        return self._state.get_events(db_name, since)


def get_event(config: Config, state: State, logger: Logger) -> Event:
    """
    Get Event Class Instance

    Args:
        config (Config): A config instance
        state (State): A state instance
        logger (Logger): A logger instance

    Returns:
        Restore: An instance of log class
    """
    return Event(config, state, logger)
