"""
Enricher to work from Github as part of `opendapi github * enrich` CLI command.
"""

# pylint: disable=unnecessary-pass, too-many-public-methods
import functools
import json
import urllib.parse
from typing import Callable, List, Optional

import click

from opendapi.adapters.dapi_server import DAPIServerResponse, FeatureValidationResult
from opendapi.cli.enrichers.base import EnricherBase
from opendapi.feature_flags import FeatureFlag, get_feature_flag
from opendapi.features import Feature, is_feature_on
from opendapi.logging import LogCounterKey, increment_counter


class FailGithubAction(click.ClickException):
    """Exception that will be raised to fail the Github action."""

    pass


class FailSilently(click.ClickException):
    """Exception that will be raised to fail silently."""

    exit_code = 0


class GithubEnricher(EnricherBase):
    """Enricher to work from Github as part of `opendapi enrich` CLI command."""

    def __init__(self, *args, **kwargs):
        """Initialize the adapter."""
        super().__init__(*args, **kwargs)
        self.feature_validate_responses: Optional[List[FeatureValidationResult]] = None

    def should_enrich(self) -> bool:
        """Should we enrich the DAPI files?"""
        return (
            self.dapi_server_config.suggest_changes
            and self.trigger_event.is_pull_request_event
        )

    def should_analyze_impact(self) -> bool:
        return self.trigger_event.is_pull_request_event and is_feature_on(
            Feature.IMPACT_ANALYSIS_V1
        )

    def print_dapi_server_progress(self, progressbar, progress: int):
        """Print the progress bar for validation."""
        progressbar.update(progress)
        self.print_markdown_and_text(
            f"\nFinished {round(progressbar.pct * 100)}% with {progressbar.format_eta()} remaining",
            color="green",
            bold=True,
        )

    @staticmethod
    def _create_summary_comment(body: str):
        """Create a summary comment."""
        header = (
            "> [!WARNING]\n"
            "> This PR updates a data schema. You are responsible for keeping schema metadata "
            "in-sync with source code and keeping stakeholders informed.\n\n"
        )
        footer = (
            "<hr>\n\n"
            "<sup>Did you find this useful? If you found a bug or have an idea to improve the "
            "DevX, [let us know](https://www.wovencollab.com/feedback)</sup>"
        )
        return f"{header}{body}{footer}"

    def _get_failed_features(self) -> List[FeatureValidationResult]:
        """Get the failed features."""
        return [
            result
            for result in (self.feature_validate_responses or [])
            if not result.passed
        ]

    def _create_feature_validation_comment_section(self) -> str:
        """Create a feature validation comment section."""
        comment_md = ""

        if (
            not get_feature_flag(FeatureFlag.FEATURE_VALIDATION_ENABLED)
            or self.feature_validate_responses is None
        ):
            return comment_md

        if not self.feature_validate_responses:
            comment_md += "# Feature Validation Passed! :tada:\n\n"
            comment_md += "No features were found to validate against.\n\n"
            return comment_md

        failed_features = self._get_failed_features()
        if not failed_features:
            comment_md += "# Feature Validation Passed! :tada:\n\n"
            comment_md += "Your files passed validation for the following features:\n"
            sorted_feature_names = sorted(
                {result.feature.value for result in self.feature_validate_responses}
            )
            comment_md += "\n".join(
                f"- {feature_name}" for feature_name in sorted_feature_names
            )
            comment_md += "\n\n"
            return comment_md

        sorted_failed_features = sorted(failed_features, key=lambda x: x.feature.value)
        comment_md += "# Feature Validation Failed"
        comment_md += (
            " :warning:\n\n"
            "Your files failed validation for the following features:\n"
        )
        for result in sorted_failed_features:
            comment_md += result.compiled_markdown
            # each one already includes newline at end
        return comment_md

    def create_or_update_summary_comment_metadata_synced(self):
        """
        Create a summary comment on the pull request for when metadata updates merged,
        though just because they were merged doesnt mean they are entirely valid
        """

        feature_validation_failed = bool(self._get_failed_features())

        if feature_validation_failed:
            pr_comment_md = "# Update your schema metadata\n\n"
            pr_comment_md += (
                "This PR contains a schema change. Suggestions from "
                f"[the portal]({self.portal_metadata_update_link}) were committed "
                "to this branch, but additional action is required to ensure your metadata "
                "passes all feature-related validation.\n\n"
            )

        else:
            pr_comment_md = "# Schema metadata synced! :tada:\n\n"
            pr_comment_md += (
                "This PR contains a schema change. Suggestions from "
                f"[the portal]({self.portal_metadata_update_link}) were committed "
                "to this branch to keep your metadata in-sync with these changes "
                "and all of your company's enabled features.\n\n"
            )

        # Impact Response
        if (
            self.analyze_impact_response
            and self.analyze_impact_response.compiled_markdown
        ):
            pr_comment_md += self.analyze_impact_response.compiled_markdown
            pr_comment_md += "\n\n"

        pr_comment_md += self._create_feature_validation_comment_section()

        self.dapi_requests.add_or_update_github_pr_comment(
            self._create_summary_comment(pr_comment_md)
        )

    def create_or_update_summary_comment_metadata_unsynced(
        self,
    ):
        """Create a summary comment on the pull request for when metadata updates not in sync"""

        # Update schema section

        link_url = self.portal_metadata_update_link
        pr_comment_md = (
            "# Update your schema metadata\n\n"
            "This PR contains a schema change. Suggestions were auto-generated "
            "to keep your metadata in-sync with these changes. "
            f"Please [visit the portal]({link_url}) to review, revise, and "
            "commit these metadata updates to this branch.\n\n"
        )
        # Review suggestion button
        pr_comment_md += (
            f'<a href="{link_url}">'
            f'<img src="{self.dapi_server_meta.suggestions_cta_url}" '
            'width="140"/></a>'
            "\n\n"
        )

        # Impact Response
        if (
            self.analyze_impact_response
            and self.analyze_impact_response.compiled_markdown
        ):
            pr_comment_md += self.analyze_impact_response.compiled_markdown
            pr_comment_md += "\n\n"

        pr_comment_md += self._create_feature_validation_comment_section()

        self.dapi_requests.add_or_update_github_pr_comment(
            self._create_summary_comment(pr_comment_md)
        )

    @functools.cached_property
    def portal_metadata_update_link(self) -> str:
        """the link to the portal metadata update page"""
        repo_path = urllib.parse.quote(self.trigger_event.repo_full_name, safe="")
        number = self.trigger_event.pull_request_number
        return urllib.parse.urljoin(
            str(self.dapi_server_meta.portal_url),
            f"/github/pull-requests/{repo_path}/{number}",
        )

    def upsert_persisted_pull_request_with_entities(self):
        """Upsert the persisted pull request on the DAPI server with the current entities."""

        # while we are dual writing, we want to capture and log all errors to sentry but
        # to keep going. Therefore we catch all exceptions, capture/log them to sentry, and
        # return in the instance of an error
        try:
            self.print_markdown_and_text(
                "\n\nBegin syncing to enable Woven Portal DevX...",
                color="green",
            )

            # the files that need to be persisted for udpating in the FE are:
            # - all files that have changed from the base commit
            # - all files that have changed from the current commit, even if
            #   they are now unchanged from the base commit
            # - plus all opendapi filetypes that are non dapis as required for features
            all_changed_filepaths_from_base = {
                loc
                for loc_to_content in self.changed_files_from_base.contents_as_dict().values()
                for loc in loc_to_content.keys()
            }
            all_changed_filepaths_from_current = {
                loc
                for loc_to_content in self.changed_files.contents_as_dict().values()
                for loc in loc_to_content.keys()
            }
            teams_filepaths = set(self.all_files.teams.keys())
            subjects_filepaths = set(self.all_files.subjects.keys())
            categories_filepaths = set(self.all_files.categories.keys())
            datastores_filepaths = set(self.all_files.datastores.keys())
            purposes_filepaths = set(self.all_files.purposes.keys())
            number_persisted_files = len(
                all_changed_filepaths_from_base
                | all_changed_filepaths_from_current
                | teams_filepaths
                | subjects_filepaths
                | categories_filepaths
                | datastores_filepaths
                | purposes_filepaths
            )

            self.print_markdown_and_text(
                f"\nPersisting {number_persisted_files} OpenDAPI files in"
                f" batch size of {self.dapi_server_config.pr_sync_batch_size}",
                color="green",
            )

            # ensure that the PR is created, which is necessary for persisting entities
            self.dapi_requests.get_or_create_gh_pull_request()

            with click.progressbar(length=number_persisted_files) as progressbar:

                def _notify(progress: int):
                    """Notify the user to the progress."""
                    return self.print_dapi_server_progress(
                        progressbar, progress
                    )  # pragma: no cover

                persisted_pr_entities = (
                    self.dapi_requests.create_gh_pull_request_entities(
                        all_files=self.all_files,
                        base_commit_files=self.base_commit_files,
                        current_commit_files=self.current_commit_files,
                        changed_files_from_base=self.changed_files_from_base,
                        changed_files=self.changed_files,
                        enriched_files=self.all_files_enriched,
                        notify_function=_notify,
                        feature_validate_responses=self.feature_validate_responses,
                    )
                )

            self.print_markdown_and_text(
                "\nSuccess!\nNow updating the Woven Portal to reflect the changes...",
                color="green",
            )

            self.dapi_requests.upsert_gh_pull_request(
                woven_comment_id=None,
                persisted_pr_entities_to_upsert=persisted_pr_entities,
            )

            self.print_markdown_and_text(
                "\nSuccess!",
                color="green",
            )

        except Exception as e:  # pylint: disable=broad-except
            self.print_markdown_and_text(str(e), color="red")
            raise e

    def create_empty_gpr(self):
        """
        To be used if the PR has no schema changes.
        We still want the GithubPullRequest to be created for the PR, and to be in sync
        with commit_shas, and we must clear it of all previous persisted_pull_request_entities
        it was associated with.
        """
        self.print_markdown_and_text(
            "\n\nThis PR has no schema changes. Logging this for Woven Portal Observability.",
            color="yellow",
        )
        self.dapi_requests.upsert_gh_pull_request(
            woven_comment_id=None,
            persisted_pr_entities_to_upsert=[],
        )

    def functions_to_run(self) -> List[Callable[[], Optional[DAPIServerResponse]]]:
        """Check if we should run the action."""
        # if this is not a pull request event, we only do things if there are files to process
        if self.trigger_event.is_push_event:
            if self._are_there_files_to_process():
                return [
                    *self.base_functions_to_run,
                    self.validate_features,
                    self.possibly_fail_github_action,
                ]
            return []

        # this is a pull request event

        # if there are files to process, so we run the entire validation and enrichment flow
        if self._are_there_files_to_process():
            return [
                *self.base_functions_to_run,
                self.validate_features,
                self.upsert_persisted_pull_request_with_entities,
                self.create_or_update_summary_comment_metadata_unsynced,
                self.possibly_fail_github_action,
            ]

        # there are no files to process, but there are schema changes, and so
        # we must comment with impact analysis etc.
        if self.changed_files_from_base.dapis:
            self.print_markdown_and_text(
                "\n\nThis PR contains schema changes, continuing with non-metadata analysis.",
                color="yellow",
            )
            return [
                self.maybe_analyze_impact,
                self.validate_features,
                # we must also update the persisted PR with the entities to ensure that the
                # head commit is up to date with the PR state, since otherwise
                # the commit will not be a fast forward, which is an issue
                # open question of if we just want to upsert with the current IDs or totally
                # rewrite the file state. since the content itself should not have changed, this
                # is the safest thing to do, since it ensures that "changed_from_current"
                # etc. is up to date. we can revisit this later if all we want to do is
                # update the head commit
                self.upsert_persisted_pull_request_with_entities,
                self.create_or_update_summary_comment_metadata_synced,
                self.possibly_fail_github_action,
            ]

        # the PR has no schema changes, we must delete opendapi comments if applicable
        # I.E. the PR had schema changes, but they were reverted, and so comment should be deleted
        self.print_markdown_and_text(
            "\n\nThis PR no longer contains schema changes. Cleaning up presence, if applicable.",
            color="yellow",
        )
        return [
            # the PR has no schema changes. We still want the GithubPullRequest to be created,
            # and to be in sync with commit_shas, and we must clear it of all
            # previous persisted_pull_request_entities it was associated with
            self.create_empty_gpr,
            self.dapi_requests.delete_github_pr_comment,
        ]

    def validate_features(self) -> Optional[List[FeatureValidationResult]]:
        """
        Validate the features.
        """

        self.print_markdown_and_text(
            "\n\nValidating features...",
            color="green",
        )

        # get the validation response
        self.feature_validate_responses = self.dapi_requests.validate_features(
            all_files=self.all_files,
            changed_files=self.changed_files,
            changed_files_from_base=self.changed_files_from_base,
            base_commit_files=self.base_commit_files,
            current_commit_files=self.current_commit_files,
        )

        return self.feature_validate_responses

    def possibly_fail_github_action(self):
        """Check if we should fail the Github action on a pull request or push"""
        error_messages = []

        if self.changed_files.dapis:
            unsynced_dapis = sorted(self.changed_files.dapis.keys())
            txt = (
                "\n\nThe following DAPIs' metadata is not in sync with schema changes:"
            )
            for dapi in unsynced_dapis:
                txt += f"\n\t- {dapi}"  # pylint: disable=consider-using-join

            self.print_markdown_and_text(
                txt,
                color="red",
            )
            error_messages.append("\n\t- Metadata is not in sync.")

        if self.validate_response and self.validate_response.errors:
            self.print_markdown_and_text(
                "\n\nYour DAPI files have validation errors, as listed "
                f"below:\n{json.dumps(self.validate_response.errors, indent=2)}",
                color="red",
            )
            error_messages.append(
                "\n\t- There are validation errors in the DAPI files."
            )

        if self._get_failed_features():
            self.print_markdown_and_text(
                "\n\nYour files have feature validation errors, as listed: "
                f"{self._create_feature_validation_comment_section()}",
                color="red",
            )
            error_messages.append(
                "\n\t- There are feature related validation errors in the DAPI files."
            )

        if error_messages:
            raise FailGithubAction("".join(error_messages))

    def run(self):
        if self.trigger_event.is_pull_request_event:
            metrics_tags = {"org_name": self.config.org_name_snakecase}
            increment_counter(LogCounterKey.USER_PR_CREATED, tags=metrics_tags)
        super().run()
