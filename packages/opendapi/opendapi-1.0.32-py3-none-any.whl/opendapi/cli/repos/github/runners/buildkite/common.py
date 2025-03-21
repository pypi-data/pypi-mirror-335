"""
Common helpers for the buildkite runner
"""

from opendapi.feature_flags import FeatureFlag, get_feature_flag


def should_skip_dbt_cloud__pr(kwargs):
    """
    Check if the `generate` command should be skipped

    Skip scenarios:
    1. If integrated with dbt Cloud
        a. Skip if pull request event and the run is the first attempt
    """
    should_wait_on_dbt_cloud = kwargs["dbt_cloud_url"] is not None
    # retry of 0 is first run
    run_attempt = int(kwargs["buildkite_retry_count"]) + 1
    # NOTE see if there is another way to get this
    is_pr_event = bool(kwargs["buildkite_pull_request"])

    return should_wait_on_dbt_cloud and is_pr_event and run_attempt == 1


def should_skip_dbt_cloud__push(kwargs):
    """
    Check if the `generate` command should be skipped

    Skip scenarios:
    1. If integrated with dbt Cloud
        a. Skip if push event - since DBT cloud doesnt run on pushes to main by default
    """
    should_wait_on_dbt_cloud = kwargs["dbt_cloud_url"] is not None
    # NOTE see if there is another way to get this
    is_push_event = not bool(kwargs["buildkite_pull_request"])

    return should_wait_on_dbt_cloud and is_push_event


def should_skip_dbt_cloud__all(kwargs):
    """
    Check if the `generate` command should be skipped

    Skip scenarios:
    1. If integrated with dbt Cloud
        a. Skip if the event is a pull request or push event
    """
    return should_skip_dbt_cloud__pr(kwargs) or should_skip_dbt_cloud__push(kwargs)


def should_skip_cicd_migration():
    """
    Check if command should be skipped due to cicd migration
    """
    return get_feature_flag(FeatureFlag.PERFORM_COMPLETE_SERVER_SIDE_CICD)
