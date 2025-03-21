"""CLI related defs"""

from enum import Enum


class SplitServerSyncPhase(Enum):
    """The phase of the split server sync process"""

    BASE_COLLECT = "base_collect"
    HEAD_COLLECT = "head_collect"
    HEAD_COLLECT_AND_SERVER_UPLOAD = "head_collect_and_server_upload"
    SERVER_UPLOAD = "sync"


class SplitGeneratePhase(Enum):
    """The phase of the split generate process"""

    BASE_COLLECT = "base_collect"
    CURRENT_COLLECT = "current_collect"
    CURRENT_COLLECT_AND_WRITE_LOCALLY = "current_collect_and_write_locally"
    WRITE_LOCALLY = "write_locally"
