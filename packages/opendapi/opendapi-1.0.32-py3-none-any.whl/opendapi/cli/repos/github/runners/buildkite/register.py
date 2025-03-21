"""
CLI for registering DAPI files: `opendapi github buildkite register`.
"""

# pylint: disable=duplicate-code

import click

from opendapi.cli.common import print_cli_output
from opendapi.cli.context_agnostic import repo_runner_register_cli
from opendapi.cli.options import (
    dapi_server_options,
    dev_options,
    minimal_schema_options,
    opendapi_run_options,
)
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.buildkite.common import (
    should_skip_cicd_migration,
)
from opendapi.cli.repos.github.runners.buildkite.options import (
    construct_change_trigger_event,
    runner_options,
)


@click.command()
# common options
@dapi_server_options
@dev_options
@minimal_schema_options
@opendapi_run_options
# github repo options
@repo_options
# github repo bk runner options
@runner_options
def cli(**kwargs):
    """
    This command will find all the DAPI files in the Github remote repo
    running on a Buildkite hosted runner:
        1. register them with the DAPI server

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """

    if should_skip_cicd_migration():
        print_cli_output(
            "Skipping register DAPI files command",
            color="yellow",
            bold=True,
        )
        return

    change_trigger_event = construct_change_trigger_event(kwargs)
    repo_runner_register_cli(change_trigger_event, None, kwargs)
