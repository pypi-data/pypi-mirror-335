"""CLI for validating and enriching DAPI files: `opendapi github github enrich`."""

import click

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


@click.command()
@minimal_schema_options
@dbt_options
@dev_options
@generation_options
@git_options
def cli(**kwargs):
    """
    Generate DAPI files for integrations specified in the OpenDAPI configuration file.

    For certain integrations such as DBT and PynamoDB, this command will also run
    additional commands in the respective integration directories to generate DAPI files.
    """

    runtime_skip_generation_at_base = kwargs[
        SKIP_RUNTIME_INTEGRATION_BASE_GENERATION_OPTION.name
    ]

    dbt_skip_generation_at_base = kwargs[
        SKIP_DBT_INTEGRATION_BASE_GENERATION_OPTION.name
    ]

    dbt_skip_generation_at_head = (
        kwargs[SKIP_DBT_INTEGRATION_HEAD_GENERATION_OPTION.name] or False
    )

    return repo_runner_generate_cli(
        runtime_skip_generation_at_base,
        dbt_skip_generation_at_base,
        dbt_skip_generation_at_head,
        kwargs,
    )
