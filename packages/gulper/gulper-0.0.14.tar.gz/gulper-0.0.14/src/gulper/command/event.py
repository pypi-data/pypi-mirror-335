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
from gulper.core import Event
from gulper.module import Output


class EventCommand:
    """
    Event Command
    """

    def __init__(self, event: Event, output: Output):
        """
        Class Constructor

        Args:
            event (Event): The event class instance
            output (Output): output class instance
        """
        self._event = event
        self._output = output
        self._event.setup()

    def list(self, db_name: Optional[str], since: Optional[str], as_json: bool):
        """
        Output a list of events

        Args:
            db_name (str): The database name
            since (str): A certain period for the backup
            as_json (bool): whether to output as JSON
        """
        try:
            events = self._event.list(db_name, since)
        except Exception as e:
            self._output.error_message(str(e), as_json)

        self._output.show_events(events, as_json)


def get_event_command(event: Event, output: Output) -> EventCommand:
    """
    Get an instance of event command

    Args:
        event (Event): An instance of event class
        output (Output): output class instance

    Returns:
        EventCommand: an instance of event command
    """
    return EventCommand(event, output)
