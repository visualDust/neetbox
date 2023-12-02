import os

from neetbox.utils.resource import ResourceLoader

from ._db import (
    HISTORY_FILE_ROOT,
    HISTORY_FILE_TYPE_NAME,
    DBConnection,
    FetchType,
    QueryCondition,
    SortType,
)

if not os.path.exists(HISTORY_FILE_ROOT):
    # create history root dir
    os.mkdir(HISTORY_FILE_ROOT)
# check if is dir
if not os.path.isdir(HISTORY_FILE_ROOT):
    raise RuntimeError(f"{HISTORY_FILE_ROOT} is not a directory.")


def get_history_file_list():
    history_file_loader = ResourceLoader(
        folder=HISTORY_FILE_ROOT, file_types=[HISTORY_FILE_TYPE_NAME], force_rescan=True
    )
    return history_file_loader.get_file_list()


def get_history_db_of_id(project_id):
    # todo handle thread safe things(?)
    conn = DBConnection(workspace_id=project_id)
    return conn


def get_history_db_of_file(path):
    conn = DBConnection(path=path)
    return conn


__all__ = [
    "FetchType",
    "SortType",
    "QueryCondition",
    "DBConnection",
    "get_history_db_of_id",
    "get_history_db_of_file",
]
