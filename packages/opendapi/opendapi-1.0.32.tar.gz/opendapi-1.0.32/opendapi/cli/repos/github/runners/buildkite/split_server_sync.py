"""
CLI for syncing Dapi file state with server for server driven CICD:
`opendapi github buildkite server-sync`.
"""

# pylint: disable=duplicate-code

import datetime

import click

from opendapi.adapters.dapi_server import CICDIntegration
from opendapi.cli.common import print_cli_output
from opendapi.cli.context_agnostic import repo_runner_split_server_sync_cli
from opendapi.cli.defs import SplitServerSyncPhase
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
    split_server_sync_options,
)
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.buildkite.common import (
    should_skip_dbt_cloud__pr,
    should_skip_dbt_cloud__push,
)
from opendapi.cli.repos.github.runners.buildkite.options import (
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
@split_server_sync_options
# github repo options
@repo_options
# github repo buildkite runner options
@runner_options
def cli(**kwargs):
    """
    This command will find all the analyzes all models and Dapi files in the Github remote
    repository given a Github hosted runner to collect them along with additional metadata
    to send to the DAPI server for server driven CICD.

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.

    This command does the above in various phases, to be compatible with runtime integrations.
    """

    if should_skip_dbt_cloud__pr(kwargs):
        print_cli_output(
            "Skipping split sync DAPI files with the server command",
            color="yellow",
            bold=True,
        )
        return

    runtime_skip_generation_at_base = (
        kwargs[SKIP_RUNTIME_INTEGRATION_BASE_GENERATION_OPTION.name] or False
    )

    dbt_skip_generation_at_base = kwargs[
        SKIP_DBT_INTEGRATION_BASE_GENERATION_OPTION.name
    ]

    dbt_skip_generation_at_head = kwargs[
        SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION.name
    ]
    if dbt_skip_generation_at_head is None:
        dbt_skip_generation_at_head = should_skip_dbt_cloud__push(kwargs)

    change_trigger_event = construct_change_trigger_event(kwargs)
    job_id = kwargs["buildkite_job_id"]
    # NOTE: we may want to make this an envvar set by the script,
    #       but this works for now. The ideal case is we pull this from BK API,
    #       which we will need anyway for DBT, but this is fine for now.
    job_started_at = datetime.datetime.now(datetime.timezone.utc)
    build_id = kwargs["buildkite_build_id"]
    retry_count = kwargs["buildkite_retry_count"]
    phase = SplitServerSyncPhase(kwargs["split_server_sync_phase"])
    repo_runner_split_server_sync_cli(
        change_trigger_event,
        lambda dr: dr.cicd_start_github_buildkite(
            job_id=job_id,
            job_started_at=job_started_at,
            build_id=build_id,
            retry_count=retry_count,
        ),
        CICDIntegration.GITHUB_BUILDKITE,
        phase,
        {
            "job_id": job_id,
            "job_started_at": job_started_at.isoformat(),
            "build_id": build_id,
            "retry_count": retry_count,
        },
        runtime_skip_generation_at_base,
        dbt_skip_generation_at_base,
        dbt_skip_generation_at_head,
        kwargs,
    )
