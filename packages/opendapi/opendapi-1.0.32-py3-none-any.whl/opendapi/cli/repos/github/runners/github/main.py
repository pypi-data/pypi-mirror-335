"""
This module contains the CLI entrypoint for CLIs invoked for a Github remote repo
given a Github hosted runner - i.e. `opendapi github github *`
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
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.github.enrich import cli as enrich_cli
from opendapi.cli.repos.github.runners.github.generate import cli as generate_cli
from opendapi.cli.repos.github.runners.github.options import (
    construct_change_trigger_event,
    runner_options,
)
from opendapi.cli.repos.github.runners.github.register import cli as register_cli
from opendapi.cli.repos.github.runners.github.run import cli as run_cli
from opendapi.cli.repos.github.runners.github.server_sync import cli as server_sync_cli
from opendapi.cli.repos.github.runners.github.split_generate import (
    cli as split_generate_cli,
)
from opendapi.cli.repos.github.runners.github.split_server_sync import (
    cli as split_server_sync_cli,
)


@click.group()
# common options
@dapi_server_options
@features_options
@git_options
@minimal_schema_options
@opendapi_run_options
# github repo options
@repo_options
# github repo github runner options
@runner_options
def cli(**kwargs):
    """
    This is the entrypoint for CLI invocations from a Github remote repo
    given a Github hosted runner.

    Please specify which OpenDapi command, and any relevant options.
    """
    change_trigger_event = construct_change_trigger_event(kwargs)
    sentry_tags = {
        "cmd": click.get_current_context().invoked_subcommand,
        "repository_type": "github",
        "runner": "github",
        "run_attempt": kwargs["github_run_attempt"],
        "common_rerun_id": kwargs["github_run_id"],
        "workspace": change_trigger_event.workspace,
        "event_name": change_trigger_event.event_type,
        "repo": change_trigger_event.repository,
        "gh_run_attempt": kwargs["github_run_attempt"],
        "gh_run_id": kwargs["github_run_id"],
    }
    repo_runner_cli(change_trigger_event, sentry_tags, kwargs)


cli.add_command(enrich_cli, name="enrich")
cli.add_command(generate_cli, name="generate")
cli.add_command(register_cli, name="register")
cli.add_command(run_cli, name="run")
cli.add_command(server_sync_cli, name="server-sync")
cli.add_command(split_generate_cli, name="split-generate")
cli.add_command(split_server_sync_cli, name="split-server-sync")
