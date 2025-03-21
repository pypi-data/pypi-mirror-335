"""
CLI for registering DAPI files: `opendapi local local register`.
"""

import click

from opendapi.cli.context_agnostic import repo_runner_register_cli
from opendapi.cli.options import (
    dapi_server_options,
    dev_options,
    minimal_schema_options,
    opendapi_run_options,
)
from opendapi.cli.repos.local.runners.local.options import (
    construct_change_trigger_event,
)


@click.command()
# common options
@dapi_server_options
@dev_options
@minimal_schema_options
@opendapi_run_options
def cli(**kwargs):
    """
    This command will find all the DAPI files in the local repository given the local runner to
        1. register them with the DAPI server

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """
    change_trigger_event = construct_change_trigger_event(kwargs)
    repo_runner_register_cli(change_trigger_event, None, kwargs)
