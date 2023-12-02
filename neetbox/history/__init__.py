import os

from neetbox.utils import ResourceLoader

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


def load_db_of_path(path):
    if not os.path.isfile(path):
        raise RuntimeError(f"{path} is not a file")
    conn = DBConnection(path=path)
    return conn


def get_db_list():
    history_file_loader = ResourceLoader(
        folder=HISTORY_FILE_ROOT, file_types=[HISTORY_FILE_TYPE_NAME], force_rescan=True
    )
    history_file_list = history_file_loader.get_file_list()
    for path in history_file_list:
        load_db_of_path(path=path)
    return DBConnection._id2dbc


def get_db_of_id(project_id):
    get_db_list()  # scan again, for possible file changes
    conn = DBConnection.of_project_id(project_id=project_id)
    return conn


__all__ = [
    "FetchType",
    "SortType",
    "QueryCondition",
    "DBConnection",
    "get_db_of_id",
    "get_db_list",
    "load_db_of_path",
]
