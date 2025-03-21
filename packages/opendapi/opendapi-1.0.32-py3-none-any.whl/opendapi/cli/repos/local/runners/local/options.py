"""
Houses options for invocation of a local runner of a local repo,
in addition for the change_trigger_event construction
"""

from opendapi.adapters.git import ChangeTriggerEvent


def construct_change_trigger_event(kwargs: dict) -> ChangeTriggerEvent:
    """
    Construct the ChangeTriggerEvent given that this a local repo and
    a local runner
    """
    return ChangeTriggerEvent(
        where="local",
        before_change_sha=kwargs["mainline_branch_name"],
        after_change_sha="HEAD",
    )
