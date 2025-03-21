"""
CLI for syncing Dapi file state with server for server driven CICD:
`opendapi github github server-sync`.
"""

# pylint: disable=duplicate-code

import click

from opendapi.adapters.dapi_server import CICDIntegration
from opendapi.cli.common import print_cli_output
from opendapi.cli.context_agnostic import repo_runner_server_sync_cli
from opendapi.cli.options import (
    SKIP_DBT_INTEGRATION_BASE_GENERATION_OPTION,
    SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION,
    SKIP_RUNTIME_INTEGRATION_BASE_GENERATION_OPTION,
    dapi_server_options,
    dbt_options,
    dev_options,
    generation_options,
    minimal_schema_options,
    opendapi_run_options,
)
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.github.common import (
    should_skip_dbt_cloud__pr,
    should_skip_dbt_cloud__push,
)
from opendapi.cli.repos.github.runners.github.options import (
    construct_change_trigger_event,
    runner_options,
)


@click.command()
# common options
@dapi_server_options
@dbt_options
@dev_options
@generation_options
@minimal_schema_options
@opendapi_run_options
# github repo options
@repo_options
# github repo github runner options
@runner_options
def cli(**kwargs):
    """
    This command will find all the analyzes all models and Dapi files in the Github remote
    repository given a Github hosted runner to collect them along with additional metadata
    to send to the DAPI server for server driven CICD.

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """

    if should_skip_dbt_cloud__pr(kwargs):
        print_cli_output(
            "Skipping sync DAPI files with the server command",
            color="yellow",
            bold=True,
        )
        return

    runtime_skip_generation_at_base = kwargs.get(
        SKIP_RUNTIME_INTEGRATION_BASE_GENERATION_OPTION.name, False
    )

    dbt_skip_generation_at_base = kwargs.get(
        SKIP_DBT_INTEGRATION_BASE_GENERATION_OPTION.name, True
    )

    dbt_skip_generation_at_head = kwargs[
        SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION.name
    ]
    if dbt_skip_generation_at_head is None:
        dbt_skip_generation_at_head = should_skip_dbt_cloud__push(kwargs)

    change_trigger_event = construct_change_trigger_event(kwargs)
    run_id = kwargs["github_run_id"]
    run_attempt = kwargs["github_run_attempt"]
    run_number = kwargs["github_run_number"]
    repo_runner_server_sync_cli(
        change_trigger_event,
        lambda dr: dr.cicd_start_github_github(
            run_id=run_id,
            run_attempt=run_attempt,
            run_number=run_number,
        ),
        CICDIntegration.GITHUB_GITHUB,
        {
            "run_id": run_id,
            "run_attempt": run_attempt,
            "run_number": run_number,
        },
        runtime_skip_generation_at_base,
        dbt_skip_generation_at_base,
        dbt_skip_generation_at_head,
        kwargs,
    )
