"""
Houses common functionality for running OpenDapi
functions - independent of repo/runner.
"""

# pylint: disable=too-many-lines

from importlib.metadata import version
from typing import Callable, Dict, Optional, Tuple, Type

import click
import sentry_sdk

from opendapi.adapters.dapi_server import (
    CICDIntegration,
    DAPIChangeNotification,
    DAPIRequests,
)
from opendapi.adapters.file import OpenDAPIFileContents
from opendapi.adapters.git import ChangeTriggerEvent
from opendapi.cli.common import (
    OpenDAPIConfig,
    Schemas,
    get_opendapi_config_from_root,
    pretty_print_errors,
    print_cli_output,
)
from opendapi.cli.defs import SplitGeneratePhase, SplitServerSyncPhase
from opendapi.cli.enrichers.base import EnricherBase
from opendapi.cli.options import (  # NOTE: see !! IMPORTANT !! note below
    BASE_COMMIT_SHA_PARAM_NAME_WITH_OPTION,
    CATEGORIES_PARAM_NAME_WITH_OPTION,
    DAPI_PARAM_NAME_WITH_OPTION,
    DATASTORES_PARAM_NAME_WITH_OPTION,
    PURPOSES_PARAM_NAME_WITH_OPTION,
    SUBJECTS_PARAM_NAME_WITH_OPTION,
    TEAMS_PARAM_NAME_WITH_OPTION,
    construct_dapi_server_config,
)
from opendapi.cli.utils import collected_files_tmp_dump, collected_files_tmp_load
from opendapi.defs import (
    DAPI_CLIENT_REQUIRED_MINIMAL_SCHEMA,
    CommitType,
    OpenDAPIEntity,
)
from opendapi.feature_flags import FeatureFlag, get_feature_flag, set_feature_flags
from opendapi.features import load_from_raw_dict, set_feature_to_status
from opendapi.logging import LogDistKey, Timer, logger, sentry_init
from opendapi.validators.defs import CollectedFile
from opendapi.validators.validate import collect_and_validate_cached
from opendapi.writers.utils import get_writer_for_entity

# NOTE think about commenting which common options are used in each command

########## main ##########


def repo_runner_cli(
    change_trigger_event: ChangeTriggerEvent,
    sentry_tags: dict,
    kwargs: dict,
):
    """
    To be used by the 'main' cli for a repo/runner combo, i.e.
    opendapi.cli.repos.github.runners.buildkite.main.cli

    Takes care of getting common information from DapiServer, setting up sentry,
    etc.
    """

    dapi_server_config = construct_dapi_server_config(kwargs)
    dapi_requests = None

    BASE_COMMIT_SHA_PARAM_NAME_WITH_OPTION.set_as_envvar_if_none(
        kwargs, change_trigger_event.before_change_sha
    )

    if not kwargs.get("skip_client_config"):
        try:
            # Initialize sentry and fetch Feature flags
            # This fails silently if the client config is not available
            # This is temporary to monitor if this actually breaks
            dapi_requests = DAPIRequests(
                dapi_server_config=dapi_server_config,
                trigger_event=change_trigger_event,
            )

            client_config = dapi_requests.get_client_config_from_server()
            sentry_tags.update(client_config.get("sentry_tags", {}))
            sentry_init(
                client_config.get("sentry", {}),
                tags=sentry_tags,
            )

            if client_config.get("fetch_feature_flags", False):
                feature_flags: dict = (
                    dapi_requests.get_client_feature_flags_from_server(
                        [f.value for f in FeatureFlag]
                    )
                )
                set_feature_flags(
                    {
                        FeatureFlag(f): val
                        for f, val in feature_flags.items()
                        if FeatureFlag.has_value(f)
                    }
                )
        except Exception as exp:  # pylint: disable=broad-except
            logger.error("Error fetching client config: %s", exp)

    all_params_present = all(
        kwargs.get(param.name) is not None
        for param in (
            CATEGORIES_PARAM_NAME_WITH_OPTION,
            DAPI_PARAM_NAME_WITH_OPTION,
            DATASTORES_PARAM_NAME_WITH_OPTION,
            PURPOSES_PARAM_NAME_WITH_OPTION,
            SUBJECTS_PARAM_NAME_WITH_OPTION,
            TEAMS_PARAM_NAME_WITH_OPTION,
        )
    )
    fetched_repo_features_info = None
    if not all_params_present and not kwargs.get("skip_server_minimal_schemas"):
        # we do not try/catch here, since if they are not set to skipped then they are required
        # for the run
        dapi_requests = dapi_requests or DAPIRequests(
            dapi_server_config=dapi_server_config,
            trigger_event=change_trigger_event,
        )
        fetched_repo_features_info = dapi_requests.get_repo_features_info_from_server()
        enabled_schemas = fetched_repo_features_info.enabled_schemas
        CATEGORIES_PARAM_NAME_WITH_OPTION.set_as_envvar_if_none(
            kwargs, enabled_schemas.categories
        )
        DAPI_PARAM_NAME_WITH_OPTION.set_as_envvar_if_none(kwargs, enabled_schemas.dapi)
        DATASTORES_PARAM_NAME_WITH_OPTION.set_as_envvar_if_none(
            kwargs, enabled_schemas.datastores
        )
        PURPOSES_PARAM_NAME_WITH_OPTION.set_as_envvar_if_none(
            kwargs, enabled_schemas.purposes
        )
        SUBJECTS_PARAM_NAME_WITH_OPTION.set_as_envvar_if_none(
            kwargs, enabled_schemas.subjects
        )
        TEAMS_PARAM_NAME_WITH_OPTION.set_as_envvar_if_none(
            kwargs, enabled_schemas.teams
        )

    raw_feature_to_status = kwargs.get("feature_to_status")
    # not set, load from dapi server
    if raw_feature_to_status is None:
        if not fetched_repo_features_info:
            dapi_requests = dapi_requests or DAPIRequests(
                dapi_server_config=dapi_server_config,
                trigger_event=change_trigger_event,
            )
            fetched_repo_features_info = (
                dapi_requests.get_repo_features_info_from_server()
            )

        feature_to_status = fetched_repo_features_info.feature_to_status

    # set, load from env var raw dict
    else:
        feature_to_status = load_from_raw_dict(raw_feature_to_status)

    set_feature_to_status(feature_to_status)


########## split_generate and split_server_sync common ##########


def _collected_files_to_tmp(
    commit_sha: Optional[str],
    commit_type: CommitType,
    runtime_skip_generation: bool,
    dbt_skip_generation: bool,
    minimal_schemas: Schemas,
    kwargs: dict,
):
    """
    Generate collected files and write them to tmp locations if no errors
    """
    state_str = (
        f"{commit_type.value} commit: {commit_sha}" if commit_sha else "current state"
    )
    print_cli_output(
        (
            "Accumulating DAPI files for your integrations per "
            f"`opendapi.config.yaml` configuration at {state_str}"
        ),
        color="green",
    )

    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"), validate_config=True
    )

    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.COLLECT_FILES, tags=metrics_tags):

        print_cli_output(
            f"Tackling {state_str}...",
            color="yellow",
        )
        collected_files, errors = collect_and_validate_cached(
            opendapi_config=opendapi_config,
            minimal_schemas=minimal_schemas,
            commit_sha=commit_sha,
            # integration specific flags
            runtime_skip_generation=runtime_skip_generation,
            dbt_skip_generation=dbt_skip_generation,
        )
        if errors:
            pretty_print_errors(errors)
            # fails with exit code 1 - meaning it blocks merging - but as a ClickException
            # it does not go to sentry, which is appropriate, as this is not an error condition
            raise click.ClickException("Encountered one or more validation errors")

    with Timer(dist_key=LogDistKey.PERSIST_COLLECTED_FILES, tags=metrics_tags):
        print_cli_output(
            "Persisting to filesystem...",
            color="yellow",
        )
        collected_files_tmp_dump(commit_type, collected_files)
        print_cli_output(
            "Successfully persisted DAPI files for your integrations",
            color="green",
        )


########## generate and split_generate common ##########


def _generate_minimal_schemas(kwargs: dict) -> Schemas:
    """Minimal schemas for generate-like commands"""
    return Schemas.create(
        teams=TEAMS_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        datastores=DATASTORES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        purposes=PURPOSES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        dapi=DAPI_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        subjects=SUBJECTS_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        categories=CATEGORIES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
    )


def _post_collected_files_generate(
    opendapi_config: OpenDAPIConfig,
    base_collected_files: Dict[OpenDAPIEntity, Dict[str, CollectedFile]],
    current_collected_files: Dict[OpenDAPIEntity, Dict[str, CollectedFile]],
    kwargs: dict,
):
    """Writing portion of generate-like commands"""
    # actually write
    always_write = kwargs.get("always_write_generated_dapis", False)
    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.WRITE_FILES, tags=metrics_tags):
        for entity, collected_files in current_collected_files.items():
            writer_cls = get_writer_for_entity(entity)
            writer = writer_cls(
                root_dir=opendapi_config.root_dir,
                collected_files=collected_files,
                override_config=opendapi_config,
                base_collected_files=base_collected_files.get(entity),
                always_write=always_write,
            )
            written, skipped = writer.write_files()
            print_cli_output(
                f"{entity.value}: {len(written)} written, {len(skipped)} skipped",
                color="green",
            )

        print_cli_output(
            "Successfully generated DAPI files for your integrations",
            color="green",
        )


########## generate ##########


def repo_runner_generate_cli(
    runtime_skip_generation_at_base: bool,
    dbt_skip_generation_at_base: bool,
    dbt_skip_generation_at_head: bool,
    kwargs: dict,
):
    """
    To be used by the 'generate' cli for a repo/runner
    combo, i.e. opendapi.cli.repos.github.runners.buildkite.generate.cli
    """
    print_cli_output(
        "Generating DAPI files for your integrations per `opendapi.config.yaml` configuration",
        color="green",
    )
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"), validate_config=True
    )

    minimal_schemas = _generate_minimal_schemas(kwargs)

    print_cli_output(
        "Generating DAPI files for your integrations...",
        color="yellow",
    )
    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.CLI_GENERATE, tags=metrics_tags):

        total_errors = []

        # if the base commit is known, determine the file state at that commit,
        # as this is useful in determining if files should be written or not
        base_commit_sha = kwargs.get(BASE_COMMIT_SHA_PARAM_NAME_WITH_OPTION.name)
        base_collected_files = {}
        if base_commit_sha:
            print_cli_output(
                "Tackling base commit...",
                color="yellow",
            )
            base_collected_files, errors = collect_and_validate_cached(
                opendapi_config=opendapi_config,
                minimal_schemas=minimal_schemas,
                commit_sha=base_commit_sha,
                # integration specific flags
                runtime_skip_generation=runtime_skip_generation_at_base,
                dbt_skip_generation=dbt_skip_generation_at_base,
            )
            total_errors.extend(errors)

        # now collect for the current state
        print_cli_output(
            "Tackling current state...",
            color="yellow",
        )
        current_collected_files, errors = collect_and_validate_cached(
            opendapi_config=opendapi_config,
            minimal_schemas=minimal_schemas,
            commit_sha=None,
            # integration specific flags
            runtime_skip_generation=False,
            dbt_skip_generation=dbt_skip_generation_at_head,
        )

        total_errors.extend(errors)

        if total_errors:
            pretty_print_errors(total_errors)
            # fails with exit code 1 - meaning it blocks merging - but as a ClickException
            # it does not go to sentry, which is appropriate, as this is not an error condition
            raise click.ClickException("Encountered one or more validation errors")

        _post_collected_files_generate(
            opendapi_config,
            base_collected_files,
            current_collected_files,
            kwargs,
        )


########## split_generate ##########


def _split_generate_current_finalize(
    dbt_skip_generation_at_head: bool,
    kwargs: dict,
):
    """
    Split generate phase where we generate CollectedFiles for current state and then finalize
    """
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"), validate_config=True
    )

    print_cli_output(
        f"Tackling {CommitType.CURRENT.value} commit...",
        color="yellow",
    )
    head_collected_files, errors = collect_and_validate_cached(
        opendapi_config=opendapi_config,
        minimal_schemas=_generate_minimal_schemas(kwargs),
        commit_sha=None,
        # integration specific flags
        runtime_skip_generation=False,
        dbt_skip_generation=dbt_skip_generation_at_head,
    )
    if errors:
        pretty_print_errors(errors)
        # fails with exit code 1 - meaning it blocks merging - but as a ClickException
        # it does not go to sentry, which is appropriate, as this is not an error condition
        raise click.ClickException("Encountered one or more validation errors")

    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.LOAD_COLLECTED_FILES, tags=metrics_tags):
        print_cli_output(
            "Loading persisted DAPI files for your integrations...",
            color="yellow",
        )
        base_collected_files = collected_files_tmp_load(CommitType.BASE, cleanup=True)
        print_cli_output(
            "Successfully loaded persisted DAPI files for your integrations",
            color="green",
        )

    _post_collected_files_generate(
        opendapi_config,
        base_collected_files,
        head_collected_files,
        kwargs,
    )


def _split_generate_finalize(
    kwargs: dict,
):
    """
    Split Generate finalize step - where we load both head_tmp and current_tmp
    collected files
    """
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"), validate_config=True
    )

    print_cli_output(
        "Loading persisted DAPI files for your integrations...",
        color="yellow",
    )

    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.LOAD_COLLECTED_FILES, tags=metrics_tags):
        base_collected_files = collected_files_tmp_load(CommitType.BASE)

    with Timer(dist_key=LogDistKey.LOAD_COLLECTED_FILES, tags=metrics_tags):
        head_collected_files = collected_files_tmp_load(
            CommitType.CURRENT, cleanup=True
        )

    print_cli_output(
        "Successfully loaded persisted DAPI files for your integrations",
        color="green",
    )

    _post_collected_files_generate(
        opendapi_config,
        base_collected_files,
        head_collected_files,
        kwargs,
    )


def repo_runner_split_generate_cli(
    phase: SplitGeneratePhase,
    runtime_skip_generation_at_base: bool,
    dbt_skip_generation_at_base: bool,
    dbt_skip_generation_at_head: bool,
    kwargs: dict,
):
    """
    To be used by the 'split-generate' cli for a repo/runner combo, i.e.
    opendapi.cli.repos.github.runners.buildkite.split_generate.cli

    Runs the generate flow in a manner that is split across multiple phases,
    to be used by runtime integrations if needed.
    """
    if phase is SplitGeneratePhase.BASE_COLLECT:
        base_commit_sha = BASE_COMMIT_SHA_PARAM_NAME_WITH_OPTION.extract_from_kwargs(
            kwargs
        )
        if not base_commit_sha:
            raise click.ClickException(  # pragma: no cover
                f"Split generate phase {phase.value} requires a base commit sha"
            )
        return _collected_files_to_tmp(
            base_commit_sha,
            CommitType.BASE,
            runtime_skip_generation_at_base,
            dbt_skip_generation_at_base,
            _generate_minimal_schemas(kwargs),
            kwargs,
        )

    if phase is SplitGeneratePhase.CURRENT_COLLECT:
        return _collected_files_to_tmp(
            None,
            CommitType.CURRENT,
            False,
            dbt_skip_generation_at_head,
            _generate_minimal_schemas(kwargs),
            kwargs,
        )

    if phase is SplitGeneratePhase.CURRENT_COLLECT_AND_WRITE_LOCALLY:
        return _split_generate_current_finalize(dbt_skip_generation_at_head, kwargs)

    if phase is SplitGeneratePhase.WRITE_LOCALLY:
        return _split_generate_finalize(kwargs)

    raise ValueError(f"Unknown phase: {phase}")  # pragma: no cover


########## enrich ##########


def repo_runner_enrich_cli(
    change_trigger_event: ChangeTriggerEvent,
    enricher_cls: Type[EnricherBase],
    metrics_tags: dict,
    markdown_file: Optional[str],
    kwargs: dict,
):
    """
    To be used by the 'enrich' cli for a repo/runner combo, i.e.
    opendapi.cli.repos.github.runners.buildkite.enrich.cli

    Actually invokes the enricher class to enrich generated Dapi files.
    """
    opendapi_config = get_opendapi_config_from_root(kwargs.get("local_spec_path"))
    dapi_server_config = construct_dapi_server_config(kwargs)
    minimal_schemas = Schemas.create(
        teams=TEAMS_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        datastores=DATASTORES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        purposes=PURPOSES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        dapi=DAPI_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        subjects=SUBJECTS_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        categories=CATEGORIES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
    )
    enricher = enricher_cls(
        config=opendapi_config,
        dapi_server_config=dapi_server_config,
        trigger_event=change_trigger_event,
        revalidate_all_files=dapi_server_config.revalidate_all_files,
        require_committed_changes=dapi_server_config.require_committed_changes,
        minimal_schemas_for_validation=minimal_schemas,
        markdown_file=markdown_file,
    )

    enricher.print_markdown_and_text(
        "\nGetting ready to validate and enrich your DAPI files...",
        color="green",
    )
    with Timer(dist_key=LogDistKey.CLI_ENRICH, tags=metrics_tags):
        enricher.run()


########## register ##########


def repo_runner_register_cli(
    change_trigger_event: ChangeTriggerEvent,
    markdown_file: Optional[str],
    kwargs: dict,
):
    """
    To be used by the 'register' cli for a repo/runner combo, i.e.
    opendapi.cli.repos.github.runners.buildkite.register.cli

    Registers Dapi files with the Dapi server.
    """
    opendapi_config = get_opendapi_config_from_root(kwargs.get("local_spec_path"))
    dapi_server_config = construct_dapi_server_config(kwargs)
    minimal_schemas = Schemas.create(
        teams=TEAMS_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        datastores=DATASTORES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        purposes=PURPOSES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        dapi=DAPI_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        subjects=SUBJECTS_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
        categories=CATEGORIES_PARAM_NAME_WITH_OPTION.extract_from_kwargs(kwargs),
    )
    dapi_requests = DAPIRequests(
        dapi_server_config=dapi_server_config,
        trigger_event=change_trigger_event,
        opendapi_config=opendapi_config,
        error_msg_handler=lambda msg: print_cli_output(
            msg,
            color="red",
            bold=True,
            markdown_file=markdown_file,
        ),
        error_exception_cls=click.ClickException,
        txt_msg_handler=lambda msg: print_cli_output(
            msg,
            color="yellow",
            bold=True,
            no_markdown=True,
        ),
        markdown_msg_handler=lambda msg: print_cli_output(
            msg,
            color="yellow",
            bold=True,
            markdown_file=markdown_file,
            no_text=True,
        ),
    )

    should_register = (
        dapi_server_config.register_on_merge_to_mainline
        and (
            change_trigger_event.where == "local"
            or (
                change_trigger_event.where == "github"
                and change_trigger_event.is_push_event
                and change_trigger_event.git_ref
                == f"refs/heads/{dapi_server_config.mainline_branch_name}"
            )
        )
        and (dapi_server_config.woven_integration_mode != "disabled")
    )

    metrics_tags = {
        "org_name": opendapi_config.org_name_snakecase,
        "where": change_trigger_event.where,
        "event_type": change_trigger_event.event_type,
        "should_register": should_register,
    }

    if not should_register:
        print_cli_output(
            "Skipping opendapi register command",
            color="yellow",
            bold=True,
        )
        return

    with Timer(dist_key=LogDistKey.CLI_REGISTER, tags=metrics_tags):
        all_files = OpenDAPIFileContents.build_from_all_files(opendapi_config)

        current_commit_files = OpenDAPIFileContents.build_from_all_files_at_commit(
            opendapi_config, change_trigger_event.after_change_sha
        )

        print_cli_output(
            f"Registering {len(all_files)} DAPI files with the DAPI server...",
            color="green",
            bold=True,
            markdown_file=markdown_file,
        )

        with click.progressbar(length=len(all_files.dapis)) as progressbar:
            register_result = dapi_requests.register(
                all_files=all_files,
                onboarded_files=current_commit_files,
                commit_hash=change_trigger_event.after_change_sha,
                source=opendapi_config.urn,
                notify_function=lambda progress: progressbar.update(progress)
                or print_cli_output(
                    f"Finished {round(progressbar.pct * 100)}% "
                    f"with {progressbar.format_eta()} remaining",
                    color="green",
                    markdown_file=markdown_file,
                ),
                minimal_schemas_for_validation=minimal_schemas,
            )

            # unregister missing dapis
            unregister_result = dapi_requests.unregister(
                source=opendapi_config.urn,
                except_dapi_urns=[dapi["urn"] for dapi in all_files.dapis.values()],
            )

            # send notifications
            total_change_notification = (
                DAPIChangeNotification.safe_merge(
                    register_result.dapi_change_notification,
                    unregister_result.dapi_change_notification,
                )
                or DAPIChangeNotification()
            )
            dapi_requests.notify(total_change_notification)

        print_cli_output(
            "Successfully registered DAPI files with the DAPI server",
            color="green",
            bold=True,
            markdown_file=markdown_file,
        )


########## run ##########


def repo_runner_run_cli(
    commands: Dict[str, click.Command],
    kwargs: dict,
):
    """
    To be used by the 'run' cli for a repo/runner combo, i.e.
    opendapi.cli.repos.github.runners.buildkite.run.cli

    Given a set of commands, runs then as long as they are not intended to be skipped
    (i.e. a third party integration may not be ready to have generate run yet)
    """
    for command_name, command in commands.items():

        print_cli_output(
            f"Invoking `{command_name}`...",
            color="green",
            bold=True,
        )
        command_params = command.params
        # run's params should always be a superset of all the children's params,
        # and therefore we do unsafe dict access as to not swallow any discrepancies
        command_kwargs = {key.name: kwargs[key.name] for key in command_params}
        with click.Context(command) as ctx:
            ctx.invoke(command, **command_kwargs)


########## server_sync and split_server_sync common ##########


def _server_sync_minimal_schemas() -> Schemas:
    """
    Returns the minimal schemas for server-driven CICD
    """
    # NOTE: Currently only DAPI schemas need minimal schemas
    #       all other schemas produced by the validators are already minimal
    return Schemas.create(
        dapi=DAPI_CLIENT_REQUIRED_MINIMAL_SCHEMA,
    )


def _post_collected_files_server_sync(  # pylint: disable=too-many-arguments, too-many-locals
    base_collected_files: Dict[OpenDAPIEntity, Dict[str, CollectedFile]],
    head_collected_files: Dict[OpenDAPIEntity, Dict[str, CollectedFile]],
    change_trigger_event: ChangeTriggerEvent,
    opendapi_config: OpenDAPIConfig,
    call_cicd_start: Callable[[DAPIRequests], Tuple[str, dict]],
    cicd_integration: CICDIntegration,
    runner_run_info: dict,
    kwargs: dict,
):
    """
    Posts the collected files to the DAPI server for server-driven CICD
    """
    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.SERVER_SYNC_TO_SERVER, tags=metrics_tags):
        dapi_server_config = construct_dapi_server_config(kwargs)
        dapi_requests = DAPIRequests(
            dapi_server_config=dapi_server_config,
            trigger_event=change_trigger_event,
        )

        print_cli_output(
            "Syncing with DAPI Server...",
            color="yellow",
        )

        total_filepaths = {
            fp
            for entity_collected in (base_collected_files, head_collected_files)
            for filepaths in entity_collected.values()
            for fp in filepaths
        }

        with click.progressbar(length=len(total_filepaths)) as progressbar:

            def _notify_progress(progress: int):
                progressbar.update(progress)
                print_cli_output(
                    (
                        f"\nFinished {round(progressbar.pct * 100)}% with"
                        f"{progressbar.format_eta()} remaining"
                    ),
                    color="green",
                    bold=True,
                )

            woven_cicd_id, s3_upload_data = call_cicd_start(dapi_requests)
            entity_to_filepath = dapi_requests.cicd_persist_files(
                # NOTE: update this when other integrations are added
                integration=cicd_integration,
                woven_cicd_id=woven_cicd_id,
                s3_upload_data=s3_upload_data,
                base_collected_files=base_collected_files,
                head_collected_files=head_collected_files,
                notify_function=_notify_progress,
            )
            metadata_file = {
                **{
                    entity.value: filepaths
                    for entity, filepaths in entity_to_filepath.items()
                },
                "run_info": {
                    "version": f"opendapi-{version('opendapi')}",
                    "integration_mode": dapi_server_config.woven_integration_mode,
                    "repo_being_configured": dapi_server_config.repo_being_configured,
                    "integration": cicd_integration.value,
                    "register_on_merge_to_mainline": (
                        dapi_server_config.register_on_merge_to_mainline
                    ),
                    "mainline_branch_name": dapi_server_config.mainline_branch_name,
                    **runner_run_info,
                },
                "opendapi_config": opendapi_config.config,
                "change_trigger_event": change_trigger_event.as_dict,
                "woven_cicd_id": woven_cicd_id,
            }
            dapi_requests.cicd_complete(
                integration=cicd_integration,
                metadata_file=metadata_file,
                woven_cicd_id=woven_cicd_id,
            )

        print_cli_output(
            "Successfully synced DAPI files for your integrations to dapi server",
            color="green",
        )


########## server_sync ##########


def repo_runner_server_sync_cli(  # pylint: disable=too-many-arguments
    change_trigger_event: ChangeTriggerEvent,
    call_cicd_start: Callable[[DAPIRequests], Tuple[str, dict]],
    cicd_integration: CICDIntegration,
    runner_run_info: dict,
    runtime_skip_generation_at_base: bool,
    dbt_skip_generation_at_base: bool,
    dbt_skip_generation_at_head: bool,
    kwargs: dict,
):  # pylint: disable=too-many-locals
    """
    To be used by the 'server-sync' cli for a repo/runner combo, i.e.
    opendapi.cli.repos.github.runners.buildkite.server_sync.cli

    Syncs Dapi file states with the Dapi server, to be used by server-driven
    CICD.
    """

    try:
        print_cli_output(
            (
                "Accumulating DAPI files for your integrations per "
                "`opendapi.config.yaml` configuration"
            ),
            color="green",
        )

        opendapi_config = get_opendapi_config_from_root(
            local_spec_path=kwargs.get("local_spec_path"), validate_config=True
        )

        minimal_schemas = _server_sync_minimal_schemas()

        metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
        with Timer(dist_key=LogDistKey.CLI_SERVER_SYNC, tags=metrics_tags):

            total_errors = []

            # first collect for the base commit
            print_cli_output(
                "Tackling base commit...",
                color="yellow",
            )
            base_collected_files, errors = collect_and_validate_cached(
                opendapi_config=opendapi_config,
                minimal_schemas=minimal_schemas,
                commit_sha=change_trigger_event.before_change_sha,
                # integration specific flags
                runtime_skip_generation=runtime_skip_generation_at_base,
                dbt_skip_generation=dbt_skip_generation_at_base,
            )
            total_errors.extend(errors)

            # now collect for the head state
            print_cli_output(
                "Tackling head commit...",
                color="yellow",
            )
            head_collected_files, errors = collect_and_validate_cached(
                opendapi_config=opendapi_config,
                minimal_schemas=minimal_schemas,
                commit_sha=change_trigger_event.after_change_sha,
                # integration specific flags
                runtime_skip_generation=False,
                dbt_skip_generation=dbt_skip_generation_at_head,
            )
            total_errors.extend(errors)

            if total_errors:
                pretty_print_errors(total_errors)
                # fails with exit code 1 - meaning it blocks merging - but as a ClickException
                # it does not go to sentry, which is appropriate, as this is not an error condition
                raise click.ClickException("Encountered one or more validation errors")

            _post_collected_files_server_sync(
                base_collected_files=base_collected_files,
                head_collected_files=head_collected_files,
                change_trigger_event=change_trigger_event,
                opendapi_config=opendapi_config,
                call_cicd_start=call_cicd_start,
                cicd_integration=cicd_integration,
                runner_run_info=runner_run_info,
                kwargs=kwargs,
            )

    # for now, swallow all errors while we migrate
    except (Exception, click.ClickException) as e:  # pylint: disable=broad-except
        print_cli_output(str(e), color="red")
        sentry_sdk.capture_exception(e)
        # but if the feature flag is on, this is a true error
        if get_feature_flag(FeatureFlag.PERFORM_COMPLETE_SERVER_SIDE_CICD):
            raise e


########## split_server_sync ##########


def _split_server_sync_head_sync(
    change_trigger_event: ChangeTriggerEvent,
    call_cicd_start: Callable[[DAPIRequests], Tuple[str, dict]],
    cicd_integration: CICDIntegration,
    runner_run_info: dict,
    dbt_skip_generation: bool,
    kwargs: dict,
):
    """
    Split Server Sync head-sync phase, where we load generated files that were persisted
    for base_tmp and then generate CollectedFiles for Head before syncing to Dapi server
    """
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"), validate_config=True
    )

    commit_sha = change_trigger_event.after_change_sha
    print_cli_output(
        f"Tackling {CommitType.HEAD.value} commit {commit_sha}...",
        color="yellow",
    )
    head_collected_files, errors = collect_and_validate_cached(
        opendapi_config=opendapi_config,
        minimal_schemas=_server_sync_minimal_schemas(),
        commit_sha=commit_sha,
        # integration specific flags
        runtime_skip_generation=False,
        dbt_skip_generation=dbt_skip_generation,
    )
    if errors:
        pretty_print_errors(errors)
        # fails with exit code 1 - meaning it blocks merging - but as a ClickException
        # it does not go to sentry, which is appropriate, as this is not an error condition
        raise click.ClickException("Encountered one or more validation errors")

    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.LOAD_COLLECTED_FILES, tags=metrics_tags):
        print_cli_output(
            "Loading persisted DAPI files for your integrations...",
            color="yellow",
        )
        base_collected_files = collected_files_tmp_load(CommitType.BASE, cleanup=True)
        print_cli_output(
            "Successfully loaded persisted DAPI files for your integrations",
            color="green",
        )

    _post_collected_files_server_sync(
        base_collected_files=base_collected_files,
        head_collected_files=head_collected_files,
        change_trigger_event=change_trigger_event,
        opendapi_config=opendapi_config,
        call_cicd_start=call_cicd_start,
        cicd_integration=cicd_integration,
        runner_run_info=runner_run_info,
        kwargs=kwargs,
    )


def _split_server_sync_sync(
    change_trigger_event: ChangeTriggerEvent,
    call_cicd_start: Callable[[DAPIRequests], Tuple[str, dict]],
    cicd_integration: CICDIntegration,
    runner_run_info: dict,
    kwargs: dict,
):
    """
    Split Server Sync sync phase, where we load generated files that were persisted
    for base_tmp and head_tmp before syncing to Dapi server
    """
    opendapi_config = get_opendapi_config_from_root(
        local_spec_path=kwargs.get("local_spec_path"), validate_config=True
    )

    print_cli_output(
        "Loading persisted DAPI files for your integrations...",
        color="yellow",
    )

    metrics_tags = {"org_name": opendapi_config.org_name_snakecase}
    with Timer(dist_key=LogDistKey.LOAD_COLLECTED_FILES, tags=metrics_tags):
        base_collected_files = collected_files_tmp_load(CommitType.BASE)

    with Timer(dist_key=LogDistKey.LOAD_COLLECTED_FILES, tags=metrics_tags):
        head_collected_files = collected_files_tmp_load(CommitType.HEAD, cleanup=True)

    print_cli_output(
        "Successfully loaded persisted DAPI files for your integrations",
        color="green",
    )

    _post_collected_files_server_sync(
        base_collected_files=base_collected_files,
        head_collected_files=head_collected_files,
        change_trigger_event=change_trigger_event,
        opendapi_config=opendapi_config,
        call_cicd_start=call_cicd_start,
        cicd_integration=cicd_integration,
        runner_run_info=runner_run_info,
        kwargs=kwargs,
    )


def repo_runner_split_server_sync_cli(  # pylint: disable=too-many-arguments
    change_trigger_event: ChangeTriggerEvent,
    call_cicd_start: Callable[[DAPIRequests], Tuple[str, dict]],
    cicd_integration: CICDIntegration,
    phase: SplitServerSyncPhase,
    runner_run_info: dict,
    runtime_skip_generation_at_base: bool,
    dbt_skip_generation_at_base: bool,
    dbt_skip_generation_at_head: bool,
    kwargs: dict,
):
    """
    To be used by the 'split-server-sync' cli for a repo/runner combo, i.e.
    opendapi.cli.repos.github.runners.buildkite.server_sync.cli

    Syncs Dapi file states with the Dapi server, but generating CollectedFiles
    in a staggered fashion, to be used for runtime integrations, if applicable.
    """
    if phase is SplitServerSyncPhase.BASE_COLLECT:
        return _collected_files_to_tmp(
            change_trigger_event.before_change_sha,
            CommitType.BASE,
            runtime_skip_generation_at_base,
            dbt_skip_generation_at_base,
            _server_sync_minimal_schemas(),
            kwargs,
        )

    if phase is SplitServerSyncPhase.HEAD_COLLECT:
        return _collected_files_to_tmp(
            change_trigger_event.after_change_sha,
            CommitType.HEAD,
            False,
            dbt_skip_generation_at_head,
            _server_sync_minimal_schemas(),
            kwargs,
        )

    if phase is SplitServerSyncPhase.HEAD_COLLECT_AND_SERVER_UPLOAD:
        return _split_server_sync_head_sync(
            change_trigger_event,
            call_cicd_start,
            cicd_integration,
            runner_run_info,
            dbt_skip_generation_at_head,
            kwargs,
        )

    if phase is SplitServerSyncPhase.SERVER_UPLOAD:
        return _split_server_sync_sync(
            change_trigger_event,
            call_cicd_start,
            cicd_integration,
            runner_run_info,
            kwargs,
        )

    raise ValueError(f"Unknown phase: {phase}")  # pragma: no cover
