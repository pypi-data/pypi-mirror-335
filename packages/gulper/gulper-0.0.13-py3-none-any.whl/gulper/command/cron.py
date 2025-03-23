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

from gulper.core import Cron


class CronCommand:
    """
    Cron Command
    """

    def __init__(self, cron: Cron):
        """
        Class Constructor

        Args:
            cron (Cron): The cron class instance
        """
        self._cron = cron
        self._cron.setup()

    def run(self, is_daemon: bool):
        """
        Run cron daemon

        Args:
            is_daemon (bool): whether to run as a daemon
        """
        return self._cron.run(is_daemon)


def get_cron_command(cron: Cron) -> CronCommand:
    """
    Get an instance of cron command

    Args:
        cron (Cron): An instance of cron class

    Returns:
        CronCommand: an instance of cron command
    """
    return CronCommand(cron)
