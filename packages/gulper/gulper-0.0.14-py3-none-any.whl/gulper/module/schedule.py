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

from cron_converter import Cron
from datetime import datetime, timezone


class Schedule:
    """
    A class for handling cron schedule operations and datetime formatting.
    """

    def get_cron_next_run(self, cron_expr: str) -> datetime:
        """
        Get the next run time for a given cron expression.

        Args:
            cron_expr (str): A string representing the cron expression.

        Returns:
            datetime: The next scheduled run time in UTC.
        """
        cron = Cron(cron_expr)
        schedule = cron.schedule(timezone_str="UTC")
        return schedule.next()

    def get_cron_prev_run(self, cron_expr: str) -> datetime:
        """
        Get the previous run time for a given cron expression.

        Args:
            cron_expr (str): A string representing the cron expression.

        Returns:
            datetime: The previous scheduled run time in UTC.
        """
        cron = Cron(cron_expr)
        schedule = cron.schedule(timezone_str="UTC")
        return schedule.prev()

    def get_current_utc(self) -> datetime:
        """
        Get the current UTC time.

        Returns:
            datetime: The current time in UTC.
        """
        return datetime.now(timezone.utc)

    def format(self, dt: datetime) -> str:
        """
        Format a datetime object to ISO 8601 string.

        Args:
            dt (datetime): The datetime object to format.

        Returns:
            str: The formatted datetime string in ISO 8601 format.
        """
        return str(dt.isoformat())


def get_schedule() -> Schedule:
    """
    Create and return a new Schedule instance.

    Returns:
        Schedule: A new instance of the Schedule class.
    """
    return Schedule()
