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

import click
from gulper import __version__
from gulper.module import get_config
from gulper.module import get_logger
from gulper.module import get_state
from gulper.module import get_file_system
from gulper.core import get_backup
from gulper.core import get_cron
from gulper.core import get_event
from gulper.core import get_restore
from gulper.command import get_backup_command
from gulper.command import get_cron_command
from gulper.command import get_restore_command
from gulper.command import get_event_command
from gulper.module import get_schedule
from gulper.module import get_output


@click.group(
    help="🐺 A Command Line Tool to Backup and Restore SQLite, MySQL and PostgreSQL!"
)
@click.version_option(version=__version__, help="Show the current version")
@click.option(
    "--config", default="/etc/config.yaml", help="Path to the configuration file"
)
@click.pass_context
def main(ctx, config):
    """Main command group for Gulper CLI."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config


@main.group()
@click.pass_context
def backup(ctx):
    """Backup related commands"""
    pass


@backup.command("list", help="List available backups.")
@click.option("--db", help="Database name")
@click.option("--since", help="Time range for listing backups")
@click.option("--json", is_flag=True, help="Return output as JSON")
@click.pass_context
def backup_list(ctx, db, since, json):
    """
    List backups

    Args:
        db (str): The database name
        since (str): The time range
        json (bool): whether to output json or not
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    backup = get_backup(config, state, logger, get_file_system())
    backup_command = get_backup_command(backup, get_output())
    return backup_command.list(db, since, json)


@backup.command("run", help="Run a backup for a specified database.")
@click.argument("db")
@click.option("--json", is_flag=True, help="Return output as JSON")
@click.pass_context
def backup_run(ctx, db, json):
    """
    Run db backup

    Args:
        db (str): The database name
        json (bool): whether to output json or not
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    backup = get_backup(config, state, logger, get_file_system())
    backup_command = get_backup_command(backup, get_output())
    return backup_command.run(db, json)


@backup.command("get", help="Retrieve details of a specific backup.")
@click.argument("backup_id")
@click.option("--json", is_flag=True, help="Return output as JSON")
@click.pass_context
def backup_get(ctx, backup_id, json):
    """
    Get backup

    Args:
        backup_id (str): The backup ID
        json (bool): whether to output json or not
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    backup = get_backup(config, state, logger, get_file_system())
    backup_command = get_backup_command(backup, get_output())
    return backup_command.get(backup_id, json)


@backup.command("delete", help="Delete a backup by its ID.")
@click.argument("backup_id")
@click.option("--json", is_flag=True, help="Return output as JSON")
@click.pass_context
def backup_delete(ctx, backup_id, json):
    """
    Delete backup

    Args:
        backup_id (str): The backup ID
        json (bool): whether to output json or not
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    backup = get_backup(config, state, logger, get_file_system())
    backup_command = get_backup_command(backup, get_output())
    return backup_command.delete(backup_id, json)


@main.group()
@click.pass_context
def restore(ctx):
    """Restore related commands"""
    pass


@restore.command("run", help="Restore a database from a specific backup.")
@click.argument("backup_id")
@click.option("--json", is_flag=True, help="Return output as JSON")
@click.pass_context
def restore_run(ctx, backup_id, json):
    """
    Restore a database with backup id

    Args:
        backup_id (str): The backup id
        json (bool): whether to output json or not
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    restore = get_restore(config, state, logger)
    restore_command = get_restore_command(restore, get_output())
    return restore_command.run(None, backup_id, json)


@restore.command("db", help="Restore a specific database.")
@click.argument("db")
@click.option("--json", is_flag=True, help="Return output as JSON")
@click.pass_context
def restore_db(ctx, db, json):
    """
    Restore the database with db name

    Args:
        db (str): The database name
        json (bool): whether to output json or not
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    restore = get_restore(config, state, logger)
    restore_command = get_restore_command(restore, get_output())
    return restore_command.run(db, None, json)


@main.command(help="Run backup schedules")
@click.option("--daemon", is_flag=True, help="Run in daemon mode")
@click.pass_context
def cron(ctx, daemon):
    """
    Run cron jobs

    Args:
        daemon (bool): whether to run as a daemon
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    backup = get_backup(config, state, logger, get_file_system())
    cron = get_cron(config, state, logger, backup, get_schedule())
    cron_command = get_cron_command(cron)
    return cron_command.run(daemon)


@main.group()
@click.pass_context
def event(ctx):
    """Event related commands"""
    pass


@event.command("list", help="List available events.")
@click.option("--db", help="Database name to filter events")
@click.option("--since", help="Time range for listing events")
@click.option("--json", is_flag=True, help="Return output as JSON")
@click.pass_context
def event_list(ctx, db, since, json):
    """
    List backup and restore events

    Args:
        db (str): The database name
        since (str): The time range
        json (bool): whether to output json or not
    """
    config = get_config(ctx.obj["config"])
    logger = get_logger(
        config.get_logging_level(),
        config.get_logging_handler(),
        config.get_logging_path(),
    )
    state = get_state(config.get_state_file())
    event = get_event(config, state, logger)
    event_command = get_event_command(event, get_output())
    return event_command.list(db, since, json)


if __name__ == "__main__":
    main()
