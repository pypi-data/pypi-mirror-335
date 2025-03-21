"""
CLI for generating, validating and enriching DAPI files: `opendapi local local run`
"""

import click

from opendapi.cli.context_agnostic import repo_runner_run_cli
from opendapi.cli.options import (
    dapi_server_options,
    dbt_options,
    dev_options,
    generation_options,
    git_options,
    minimal_schema_options,
    opendapi_run_options,
)
from opendapi.cli.repos.local.runners.local.enrich import cli as enrich_cli
from opendapi.cli.repos.local.runners.local.generate import cli as generate_cli
from opendapi.cli.repos.local.runners.local.register import cli as register_cli


@click.command()
# common options
@dapi_server_options
@dbt_options
@dev_options
@generation_options
@git_options
@minimal_schema_options
@opendapi_run_options
def cli(**kwargs):
    """
    This command combines the `generate`, `enrich`, and `register` commands
    conditionally for a local repo and local runner.

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """

    # Run register last to ensure the DAPI files are registered and unregistered
    # Register will also validate the DAPI files in the backend
    commands = {
        "generate": generate_cli,
        "enrich": enrich_cli,
        "register": register_cli,
    }

    repo_runner_run_cli(commands, kwargs)
