"""
This module contains the CLI entrypoint for CLIs invoked for a local repo
given a local runner - i.e. `opendapi local local *`
"""

import click

from opendapi.cli.context_agnostic import repo_runner_cli
from opendapi.cli.options import (
    dapi_server_options,
    features_options,
    git_options,
    minimal_schema_options,
    opendapi_run_options,
)
from opendapi.cli.repos.local.runners.local.enrich import cli as enrich_cli
from opendapi.cli.repos.local.runners.local.generate import cli as generate_cli
from opendapi.cli.repos.local.runners.local.options import (
    construct_change_trigger_event,
)
from opendapi.cli.repos.local.runners.local.register import cli as register_cli
from opendapi.cli.repos.local.runners.local.run import cli as run_cli
from opendapi.cli.repos.local.runners.local.split_generate import (
    cli as split_generate_cli,
)


@click.group()
# common options
@dapi_server_options
@features_options
@git_options
@minimal_schema_options
@opendapi_run_options
def cli(**kwargs):
    """
    This is the entrypoint for CLI invocations from a local repository
    given a local runner.

    Please specify which OpenDapi command, and any relevant options.
    """
    change_trigger_event = construct_change_trigger_event(kwargs)
    sentry_tags = {
        "cmd": click.get_current_context().invoked_subcommand,
        "repository_type": "local",
        "runner": "local",
    }
    repo_runner_cli(change_trigger_event, sentry_tags, kwargs)


cli.add_command(enrich_cli, name="enrich")
cli.add_command(generate_cli, name="generate")
cli.add_command(register_cli, name="register")
cli.add_command(run_cli, name="run")
cli.add_command(split_generate_cli, name="split-generate")
