"""CLI for validating and enriching DAPI files: `opendapi local local enrich`."""

import click

from opendapi.cli.common import get_opendapi_config_from_root
from opendapi.cli.context_agnostic import repo_runner_enrich_cli
from opendapi.cli.options import (
    dapi_server_options,
    dev_options,
    minimal_schema_options,
    opendapi_run_options,
)
from opendapi.cli.repos.local.enrichers.base import LocalEnricher
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
    This command will find all the DAPI files in the local repository given a local runner to
        1. validate them for compliance with the company policies
        2. enrich data semantics and classification using AI.
        3. pull forward downstream impact of the changes.

    This interacts with the DAPI server, and thus needs
    the server host and API key as environment variables or CLI options.
    """
    opendapi_config = get_opendapi_config_from_root(kwargs.get("local_spec_path"))
    change_trigger_event = construct_change_trigger_event(kwargs)

    metrics_tags = {
        "org_name": opendapi_config.org_name_snakecase,
        "where": change_trigger_event.where,
        "event_type": change_trigger_event.event_type,
    }
    repo_runner_enrich_cli(
        change_trigger_event, LocalEnricher, metrics_tags, None, kwargs
    )
