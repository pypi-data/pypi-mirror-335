"""DBT Cloud mixin for dapi_validator"""

# pylint: disable=too-few-public-methods, too-many-locals

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urlencode, urljoin

import requests

from opendapi.cli.common import print_cli_output
from opendapi.logging import logger

DBT_CLOUD_RUN_SUCCESS_STATUS = 10  # This means that the job has completed


@dataclass
class DBTCloudProject:
    """DBT Cloud project"""

    project_id: int
    account_id: int
    repo_name: str
    subdirectory: Optional[str] = None
    docs_job_id: Optional[int] = None


class DBTCloudMixin:
    """
    A mixin plugin used for adding dbt_cloud support to DBT DAPI validator.
    This plugin helps with downloading the dbt models from dbt cloud.
    """

    _dbt_commit_sha: Optional[str]

    def _dbt_cloud_request(self, uri_path: str) -> requests.Response:
        """Make a request to the DBT Cloud API"""
        dbt_cloud_url = os.environ["DAPI_DBT_CLOUD_URL"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {os.environ['DAPI_DBT_CLOUD_API_TOKEN']}",
        }

        response = requests.get(
            urljoin(dbt_cloud_url, uri_path), headers=headers, timeout=10
        )
        response.raise_for_status()
        return response

    def _validate_json_response(self, response: requests.Response) -> None:
        response = response.json()

        if response["status"]["code"] != 200 or not response["status"]["is_success"]:
            logger.error("DBT Cloud API request failed: %s", response)
            raise RuntimeError("DBT Cloud API request failed")

    def _dbt_cloud_api_request(self, uri_path: str) -> Dict:
        response = self._dbt_cloud_request(uri_path)
        self._validate_json_response(response)
        return response.json()["data"]

    def _get_latest_run(
        self,
        account_id: int,
        project_id: int,
        match_git_sha: Optional[str] = None,
        job_id: Optional[int] = None,
        ci_only: bool = True,
    ) -> Optional[Dict]:
        """Get latest run of dbt Cloud for a given project, optionally matching git sha or job ID"""
        base_url = f"/api/v2/accounts/{account_id}/runs"
        params = {
            "project_id": project_id,
            "status": DBT_CLOUD_RUN_SUCCESS_STATUS,
            # to be used later to filter by PR number
            "include_related": ["trigger", "job"],
            "order_by": "-created_at",
            "limit": 100,
            "offset": 0,
        }
        if job_id:
            params["job_definition_id"] = job_id

        match_run = None
        for idx in range(os.environ.get("DAPI_DBT_CLOUD_MAX_ITERATIONS", 20)):
            params["offset"] = idx * params["limit"]
            runs = self._dbt_cloud_api_request(base_url + "/?" + urlencode(params))
            match_run = next(
                (
                    r
                    for r in runs
                    if (
                        # NOTE: there are diff artifacts depending on how it was triggered,
                        #       and rn we can only handle CI, so skip others, unless
                        #       intended by knowing job_id
                        (not ci_only or r["job"]["job_type"] == "ci")
                        and r.get("has_docs_generated")
                        and ((r["git_sha"] == match_git_sha) or not match_git_sha)
                    )
                ),
                None,
            )
            if match_run or not runs:
                # End early if no more runs found
                break
        return match_run

    def _get_all_dbt_cloud_projects(self) -> Dict[str, DBTCloudProject]:
        """Get the DBT Cloud projects"""
        dbt_cloud_projects = []
        accounts = self._dbt_cloud_api_request("/api/v2/accounts/")
        current_repo_name = os.environ["GITHUB_REPOSITORY"]

        for account in accounts:
            projects = self._dbt_cloud_api_request(
                f"/api/v2/accounts/{account['id']}/projects/"
            )

            for project in projects:
                repo_name = project["repository"]["full_name"]
                repo_subdirectory = project.get("dbt_project_subdirectory")
                docs_job_id = project.get("docs_job_id")

                if repo_name != current_repo_name:
                    continue

                dbt_cloud_projects.append(
                    DBTCloudProject(
                        project_id=project["id"],
                        account_id=account["id"],
                        repo_name=repo_name,
                        subdirectory=repo_subdirectory or "",
                        docs_job_id=docs_job_id,
                    )
                )

        return dbt_cloud_projects

    def _write_artifact(self, artifact_path: str, content: str) -> None:
        """Write the artifact to the file system"""
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        with open(artifact_path, "w", encoding="utf-8") as fp:
            fp.write(content)

    def _download_artifact(
        self, artifact_name: str, account_id: int, run_id: int, download_path: str
    ) -> str:
        """Download the artifact from dbt cloud"""
        base_url = f"/api/v2/accounts/{account_id}/runs"
        artifacts_url = f"{base_url}/{run_id}/artifacts/"
        artifact_url = f"{artifacts_url}{artifact_name}"
        content = self._dbt_cloud_request(artifact_url).text

        if os.path.exists(download_path):
            print_cli_output(
                f"Artifact exists. Overwriting: {download_path}", color="yellow"
            )

        print_cli_output(f"Downloading artifact {artifact_name} to {download_path}")
        self._write_artifact(download_path, content)

        return download_path

    def _merge_catalogs(
        self, base_catalog_path: str, merging_catalog_path: str, output_path: str
    ) -> str:
        """Merge the catalogs"""
        with open(base_catalog_path, "r", encoding="utf-8") as fp:
            base_catalog = json.load(fp)

        with open(merging_catalog_path, "r", encoding="utf-8") as fp:
            merging_catalog = json.load(fp)

        merged_catalog = base_catalog.copy()

        # Overwrite models that exist in both catalogs - merging catalog takes precedence
        for model in merged_catalog["nodes"]:
            if model in merging_catalog["nodes"]:
                merged_catalog["nodes"][model] = merging_catalog["nodes"][model]

        # Add models that exist in merging catalog but not in base catalog
        for model in merging_catalog["nodes"]:
            if model not in merged_catalog["nodes"]:
                merged_catalog["nodes"][model] = merging_catalog["nodes"][model]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fp:
            json.dump(merged_catalog, fp)
        return output_path

    def _sync_dbt_cloud_artifacts(
        self, projects: List["DBTProjectInfo"], commit_sha: str
    ) -> bool:
        """Sync the dbt projects from dbt cloud"""

        count = 0
        dbt_cloud_projects = self._get_all_dbt_cloud_projects()
        for dbt_cloud_project in dbt_cloud_projects:
            for project in projects:
                if not project.full_path.endswith(dbt_cloud_project.subdirectory):
                    continue

                match_run = self._get_latest_run(
                    dbt_cloud_project.account_id,
                    dbt_cloud_project.project_id,
                    commit_sha,
                )

                if match_run:
                    # Download manifest
                    self._download_artifact(
                        project.manifest_filename,
                        dbt_cloud_project.account_id,
                        match_run["id"],
                        project.manifest_path,
                    )

                    # Download catalog
                    self._download_artifact(
                        project.catalog_filename,
                        dbt_cloud_project.account_id,
                        match_run["id"],
                        project.catalog_path,
                    )

                    # Download production catalog
                    if dbt_cloud_project.docs_job_id:
                        production_docs_run = self._get_latest_run(
                            dbt_cloud_project.account_id,
                            dbt_cloud_project.project_id,
                            job_id=dbt_cloud_project.docs_job_id,
                            ci_only=False,
                        )
                        if production_docs_run:
                            self._download_artifact(
                                project.catalog_filename,
                                dbt_cloud_project.account_id,
                                production_docs_run["id"],
                                project.production_catalog_path,
                            )

                            # Merge the PR catalog on top of the production catalog
                            self._merge_catalogs(
                                base_catalog_path=project.production_catalog_path,
                                merging_catalog_path=project.catalog_path,
                                output_path=project.catalog_path,
                            )

                    count += 1

        return count == len(dbt_cloud_projects)

    def _cleanup_dbt_cloud_file_state(
        self, projects: Dict[str, "DBTProjectInfo"]
    ) -> None:
        """Cleanup the dbt cloud file state"""
        for project in projects:
            for filepath in (
                project.manifest_path,
                project.catalog_path,
                project.production_catalog_path,
            ):
                if os.path.exists(filepath):
                    os.remove(filepath)

    def sync_dbt_cloud_artifacts(self, projects: Dict[str, "DBTProject"]) -> bool:
        """Sync the dbt projects from dbt cloud with a retry"""

        if not os.environ.get("DAPI_DBT_CLOUD_API_TOKEN") or not os.environ.get(
            "DAPI_DBT_CLOUD_URL"
        ):
            logger.info("DBT Cloud API token or URL not found")
            return False

        if not self._dbt_commit_sha or not os.environ.get("GITHUB_REPOSITORY"):
            logger.info("GITHUB_HEAD_SHA or GITHUB_REPOSITORY not found")
            return False

        # Keep retrying for a bit till we get the artifacts
        # By default, we will retry every 30 seconds for 2 minutes
        retry_count = int(os.environ.get("DAPI_DBT_CLOUD_RETRY_COUNT") or 30)
        retry_count = 0 if retry_count < 0 else retry_count
        retry_wait_secs = int(os.environ.get("DAPI_DBT_CLOUD_RETRY_INTERVAL") or 4)

        while retry_count >= 0:
            print_cli_output("Attempting to sync dbt cloud artifacts")

            if self._sync_dbt_cloud_artifacts(projects, self._dbt_commit_sha):
                return True

            print_cli_output("Couldn't find any artifacts")
            if retry_count > 0:
                print_cli_output(f"Retrying {retry_count} more time(s)")
                time.sleep(retry_wait_secs)

            retry_count -= 1

        return False
