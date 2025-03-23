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

import json
from typing import Dict, Any
from rich.table import Table
from rich import print as fprint
from rich.console import Console
from rich.markdown import Markdown


class Output:
    """
    Output Class
    """

    def __init__(self):
        """
        Class Constructor
        """
        self._console = Console()

    def regular_message(self, message: str, as_json: bool):
        """
        Print a regular message

        Args:
            message (str): The message to show
            as_json (bool): Whether to output as json
        """
        if as_json:
            print(json.dumps({"message": message}))
        else:
            fprint(f"[bold green]{message}[/bold green]")
        exit(0)

    def success_message(self, message: str, as_json: bool):
        """
        Print a success message

        Args:
            message (str): The message to show
            is_json (bool): Whether to output as json
        """
        if as_json:
            print(json.dumps({"message": message}))
        else:
            fprint(f"[bold green][SUCCESS][/bold green] {message}")
        exit(0)

    def error_message(self, message: str, as_json: bool):
        """
        Print an error message

        Args:
            message (str): The message to show
            as_json (bool): Whether to output as json
        """
        if as_json:
            print(json.dumps({"message": message}))
        else:
            fprint(f"[bold red][ERROR][/bold red] {message}")
        exit(1)

    def show_backups(self, data: list[Dict[str, Any]], as_json: bool):
        """
        Show Backups list

        Args:
            data (list[Dict[str, Any]]): A list of backups
            as_json (bool): Whether to output as json
        """
        if as_json:
            items = []
            for item in data:
                items.append(
                    {
                        "id": item["id"],
                        "db": item["db"],
                        "status": item["status"],
                        "createdAt": item["createdAt"],
                        "updatedAt": item["updatedAt"],
                    }
                )
            print(json.dumps(items))
            return

        # Create a table
        table = Table(title="Database Backups")

        # Add columns
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Database Name", style="magenta")
        table.add_column("Status", justify="center", style="green")
        table.add_column("Created At (UTC)", style="yellow")
        table.add_column("Updated At (UTC)", style="yellow")

        # Add rows to the table
        for item in data:
            table.add_row(
                item["id"],
                item["db"],
                item["status"].title(),
                item["createdAt"],
                item["updatedAt"],
            )

        self._console.print(table)
        exit(0)

    def show_backup(self, data: Dict[str, Any], as_json: bool):
        """
        Show Backup

        Args:
            data (Dict[str, Any]]: A backup data
            as_json (bool): Whether to output as json
        """
        if as_json:
            print(
                json.dumps(
                    {
                        "id": data.get("id"),
                        "db": data.get("db"),
                        "status": data.get("status"),
                        "backups": data.get("meta").get("backups"),
                        "backupExists": data.get("backups_exists"),
                        "createdAt": data.get("createdAt"),
                        "updatedAt": data.get("updatedAt"),
                    }
                )
            )
            return

        data["status"] = data.get("status").title()
        markdown = f"""- **Backup ID**: {data.get("id")}
- **Database**:  {data.get("db")}
- **Status**:  {data.get("status")}
- **Backups Exists**: {data.get("backups_exists")}
- **Created At**:  {data.get("createdAt")}
- **Updated At**:  {data.get("updatedAt")}
"""

        for file in data["meta"]["backups"]:
            markdown += f"- **{file.get('storage_name')}**: {file.get('file')}\n"

        md = Markdown(markdown)
        self._console.print(md)
        exit(0)

    def show_events(self, data: list[Dict[str, Any]], as_json: bool):
        """
        Show Events list

        Args:
            data (list[Dict[str, Any]]): A list of events
            as_json (bool): Whether to output as json
        """
        if as_json:
            items = []
            for item in data:
                items.append(
                    {
                        "id": item.get("id"),
                        "db": item.get("db"),
                        "type": item.get("type"),
                        "record": item.get("record"),
                        "createdAt": item.get("createdAt"),
                        "updatedAt": item.get("updatedAt"),
                    }
                )
            print(json.dumps(items))
            return

        # Create a table
        table = Table(title="Events")

        # Add columns
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Database Name", style="magenta")
        table.add_column("Type", style="red")
        table.add_column("Record", style="green")
        table.add_column("Created At (UTC)", style="yellow")
        table.add_column("Updated At (UTC)", style="yellow")

        # Add rows to the table
        for item in data:
            table.add_row(
                item.get("id"),
                item.get("db"),
                item.get("type"),
                item.get("record"),
                item.get("createdAt"),
                item.get("updatedAt"),
            )

        self._console.print(table)
        exit(0)


def get_output() -> Output:
    """
    Get an instance of output class

    Returns:
        Output: an instance of output class
    """
    return Output()
