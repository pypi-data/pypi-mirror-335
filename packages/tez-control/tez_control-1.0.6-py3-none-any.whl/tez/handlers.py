import os, subprocess

from fabric import Connection

from .config import load_config
from .colored_print import colored_print


def action_custom_server_command(terminal_command: str, settings=None, server=None):
    """
    Connects to the server, and do given commands
    """
    settings = settings if settings else load_config()
    server_host = settings.server.host
    server_user = settings.server.user
    server_password = settings.server.password
    conn = server if server else Connection(
        host=server_host,
        user=server_user,
        connect_kwargs={"password": server_password}
    )
    with conn:
        result = conn.run(terminal_command)
        colored_print(result.stdout, 'green')


def action_custom_local_command(terminal_command: str, settings=None, server=None):
    """
    Executes a local shell command.
    """
    result = subprocess.run(terminal_command, shell=True, capture_output=True, text=True)
    if result.stdout:
        colored_print(result.stdout.strip(), 'green')
    if result.stderr:
        colored_print(result.stderr.strip(), 'red')
