"""CLI for validating and enriching DAPI files: `opendapi github buildkite enrich`."""

# pylint: disable=duplicate-code

import click

from opendapi.cli.common import get_opendapi_config_from_root, print_cli_output
from opendapi.cli.context_agnostic import repo_runner_enrich_cli
from opendapi.cli.options import (
    construct_dapi_server_config,
    dapi_server_options,
    dbt_options,
    dev_options,
    minimal_schema_options,
    opendapi_run_options,
)
from opendapi.cli.repos.github.enrichers.base import GithubEnricher
from opendapi.cli.repos.github.enrichers.shadow import GithubShadowModeEnricher
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.buildkite.common import (
    should_skip_cicd_migration,
    should_skip_dbt_cloud__all,
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
@minimal_schema_options
@opendapi_run_options
# github repo options
@repo_options
# github repo bk runner options
@runner_options
def cli(**kwargs):
    """
    This command will find all the DAPI files in the Github remote repository
    given a Buildkite hosted runner to
        1. validate them for compliance with the company policies
        2. enrich data semantics and classification using AI.
        3. pull forward downstream impact of the changes.

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """

    if should_skip_cicd_migration() or should_skip_dbt_cloud__all(kwargs):
        print_cli_output(
            "Skipping validate and enrich DAPI files command",
            color="yellow",
            bold=True,
        )
        return

    opendapi_config = get_opendapi_config_from_root(kwargs.get("local_spec_path"))
    dapi_server_config = construct_dapi_server_config(kwargs)
    change_trigger_event = construct_change_trigger_event(kwargs)
    enricher_cls = (
        GithubShadowModeEnricher
        if dapi_server_config.is_repo_in_shadow_mode
        else GithubEnricher
    )

    metrics_tags = {
        "org_name": opendapi_config.org_name_snakecase,
        "where": change_trigger_event.where,
        "event_type": change_trigger_event.event_type,
    }
    repo_runner_enrich_cli(
        change_trigger_event, enricher_cls, metrics_tags, None, kwargs
    )
