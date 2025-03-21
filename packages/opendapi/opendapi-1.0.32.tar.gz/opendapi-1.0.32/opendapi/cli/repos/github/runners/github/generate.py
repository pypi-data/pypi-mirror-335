"""CLI for validating and enriching DAPI files: `opendapi github github enrich`."""

# pylint: disable=duplicate-code

import click

from opendapi.cli.common import print_cli_output
from opendapi.cli.context_agnostic import repo_runner_generate_cli
from opendapi.cli.options import (
    SKIP_DBT_INTEGRATION_BASE_GENERATION_OPTION,
    SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION,
    SKIP_RUNTIME_INTEGRATION_BASE_GENERATION_OPTION,
    dbt_options,
    dev_options,
    generation_options,
    git_options,
    minimal_schema_options,
)
from opendapi.cli.repos.github.options import repo_options
from opendapi.cli.repos.github.runners.github.common import (
    should_skip_cicd_migration,
    should_skip_dbt_cloud__all,
)
from opendapi.cli.repos.github.runners.github.options import runner_options


@click.command()
@minimal_schema_options
@dbt_options
@dev_options
@generation_options
@git_options
# github repo options
@repo_options
# github repo github runner options
@runner_options
def cli(**kwargs):
    """
    Generate DAPI files for integrations specified in the OpenDAPI configuration file.

    For certain integrations such as DBT and PynamoDB, this command will also run
    additional commands in the respective integration directories to generate DAPI files.
    """
    if should_skip_cicd_migration() or should_skip_dbt_cloud__all(kwargs):
        print_cli_output(
            "Skipping generate DAPI files command",
            color="yellow",
            bold=True,
        )
        return

    runtime_skip_generation_at_base = kwargs[
        SKIP_RUNTIME_INTEGRATION_BASE_GENERATION_OPTION.name
    ]

    dbt_skip_generation_at_base = kwargs[
        SKIP_DBT_INTEGRATION_BASE_GENERATION_OPTION.name
    ]

    dbt_skip_generation_at_head = (
        kwargs[SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION.name] or False
    )

    repo_runner_generate_cli(
        runtime_skip_generation_at_base,
        dbt_skip_generation_at_base,
        dbt_skip_generation_at_head,
        kwargs,
    )
