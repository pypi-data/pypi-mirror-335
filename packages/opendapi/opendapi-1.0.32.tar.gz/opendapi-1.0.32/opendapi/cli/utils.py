"""
Utility functions for the OpenDAPI CLI
"""

import json
import os
from typing import Dict

from opendapi.defs import CommitType, OpenDAPIEntity
from opendapi.validators.defs import CollectedFile

# NOTE: We purposefully do not use tmpfile here for two main reasons:
#       1. While we can add `prefix` and `suffix`, the exact filename is not known,
#          and since we need to persist the files across two invocations of the CLI,
#          it would add some complications in getting the files (would need to
#          examine the files in the directory, check for the prefix, etc.)
#       2. This is likely to be used within docker containers, and so we need the written
#          files to be accessible between the two containers - which would mean
#          mounting a volume. We already would have one volume mounted for the repo state,
#          so we can just use that volume for the persisted files as well (which is what this
#          code does) - otherwise we would need to mount a volume for the tmp files as well,
#          which is not necessarily OS-agnostic, and takes more setup, etc.
_PERSITED_COLLECTED_FILES_DIR = ".opendapi/cicd/persisted_collected_files/"


def _create_persisted_collected_files_filepath(commit_type: CommitType) -> str:
    return f"{_PERSITED_COLLECTED_FILES_DIR}{commit_type.value}.json"


def collected_files_tmp_dump(
    commit_type: CommitType,
    collected_files: Dict[OpenDAPIEntity, Dict[str, CollectedFile]],
) -> None:
    """Persist the collected files to the tmp directory"""
    os.makedirs(_PERSITED_COLLECTED_FILES_DIR, exist_ok=True)
    as_json = {
        entity.value: {
            filepath: collected.as_json
            for filepath, collected in filepaths_to_collected.items()
        }
        for entity, filepaths_to_collected in collected_files.items()
    }
    filepath = _create_persisted_collected_files_filepath(commit_type)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(as_json, file)


def collected_files_tmp_load(
    commit_type: CommitType,
    cleanup: bool = False,
) -> Dict[OpenDAPIEntity, Dict[str, CollectedFile]]:
    """Load the collected files from the tmp directory"""
    filepath = _create_persisted_collected_files_filepath(commit_type)
    with open(filepath, "r", encoding="utf-8") as file:
        as_json = json.load(file)

    if cleanup:
        cleanup_tmp_state()

    return {
        OpenDAPIEntity(entity): {
            filepath: CollectedFile.from_dict(collected)
            for filepath, collected in filepaths_to_collected.items()
        }
        for entity, filepaths_to_collected in as_json.items()
    }


def cleanup_tmp_state() -> None:
    """Cleanup the tmp state"""
    # delete the files
    for commit_type in CommitType:
        filepath = _create_persisted_collected_files_filepath(commit_type)
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

    # delete the dirs. this time we raise an error since
    # we expect the dirs to be there and be empty
    os.rmdir(_PERSITED_COLLECTED_FILES_DIR)
