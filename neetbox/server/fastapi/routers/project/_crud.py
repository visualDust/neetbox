# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240109

from typing import Optional, Union

from fastapi import APIRouter, Body, File, Form, HTTPException, Response, UploadFile

from neetbox._protocol import *
from neetbox.logging import Logger, LogLevel

from ....db.project.condition import ProjectDbQueryCondition
from ._bridge import Bridge

logger = Logger("Project APIs", skip_writers_names=["ws"])
logger.log_level = LogLevel.DEBUG

router = APIRouter()


@router.get(f"/list")
async def get_status_of_all_proejcts():
    return [_project_status_from_bridge(bridge) for _, bridge in Bridge.items()]


@router.get(f"/{{project_id}}")
async def get_status_of_project_id(project_id: str):
    if not Bridge.has(project_id):
        raise HTTPException(status_code=404, detail={ERROR_KEY: "Project ID not found"})
    bridge = Bridge.of_id(project_id)
    return _project_status_from_bridge(bridge)


def _project_status_from_bridge(bridge: Bridge):
    run_id_info_list = bridge.get_run_ids()
    name_of_project = None
    for run_id_info in reversed(run_id_info_list):
        config = bridge.get_status(run_id=run_id_info[RUN_ID_KEY], series="config")
        if NAME_KEY in config:
            name_of_project = config[NAME_KEY]
            break
    return {
        PROJECT_ID_KEY: bridge.project_id,
        "storage": bridge.historyDB.size,
        "online": bridge.is_online(),
        NAME_KEY: name_of_project,
        "runids": run_id_info_list,
    }


def get_history_json_of(project_id: str, table_name: str, condition=Union[dict, str]):
    if not Bridge.has(project_id):
        raise HTTPException(status_code=404, detail={ERROR_KEY: "Project ID not found"})
    try:
        if isinstance(condition, str):
            condition = json.loads(condition)
        if isinstance(condition, dict):
            condition = ProjectDbQueryCondition.loads(condition)
    except Exception as e:  # if failed to parse
        error_message = f"failed to parse condition from {type(condition)}{condition} :{e}"
        logger.debug(error_message, series="400")
        raise HTTPException(status_code=400, detail={ERROR_KEY: error_message})
    return Bridge.of_id(project_id).read_json_from_history(
        table_name=table_name, condition=condition
    )


@router.get(f"/{{project_id}}/log")
async def get_history_log_of(project_id: str, condition: str):
    return get_history_json_of(
        project_id=project_id,
        table_name=LOG_TABLE_NAME,
        condition=condition,
    )


@router.get(f"/{{project_id}}/hardware")
async def get_history_hardware_info_of(project_id: str, condition: str):
    return get_history_json_of(
        project_id=project_id,
        table_name=EVENT_TYPE_NAME_HARDWARE,
        condition=condition,
    )


@router.get(f"/{{project_id}}/series/{{table_name}}")
async def get_series_list_of(
    project_id: str, table_name: str, run_id: str = None
):  # client side function
    if not Bridge.has(project_id):
        raise HTTPException(status_code=404, detail={ERROR_KEY: "Project ID not found"})
    result = Bridge.of_id(project_id).get_series_of(table_name, run_id=run_id)
    return result


@router.get(f"/{{project_id}}/run/{{run_id}}")
async def get_status_of(project_id, run_id):
    if not Bridge.has(project_id):
        raise HTTPException(status_code=404, detail={ERROR_KEY: "Project ID not found"})
    result = Bridge.of_id(project_id).get_status(run_id=run_id)
    return result


@router.put(f"/{{project_id}}/run/{{run_id}}")
async def set_get_metadata_of_run_id(project_id: str, run_id: str, metadata: dict = Body(...)):
    bridge = Bridge.of_id(project_id)
    try:
        metadata_in_db = bridge.historyDB.fetch_metadata_of_run_id(
            run_id=run_id
        )  # get old metadata
        metadata_in_db.update(metadata)
        # Assuming the method to update metadata in your database might look like this
        # bridge.historyDB.update_metadata_of_run_id(run_id=run_id, metadata=old_metadata)
        return bridge.historyDB.fetch_metadata_of_run_id(run_id=run_id, metadata=metadata_in_db)
    except Exception as e:  # Replace with your specific database exception
        logger.debug(f"failed to update metadata of run_id {run_id}: {e}")
        raise HTTPException(status_code=404, detail={ERROR_KEY: str(e)})


@router.delete(f"/{{project_id}}/run/{{run_id}}")
async def delete_run_id(project_id: str, run_id: str):
    bridge = Bridge.of_id(project_id)
    if bridge.is_online(run_id):  # cannot delete running projects
        raise HTTPException(status_code=400, detail={ERROR_KEY: "can only delete history run id."})
    bridge.historyDB.delete_run_id(run_id)
    if 0 == len(bridge.get_run_ids()):  # check if all the run ids are deleted
        del Bridge._id2bridge[project_id]  # delete the empty bridge
    return {RESULT_KEY: "success"}


@router.post(f"/{{project_id}}/image")
async def upload_image(project_id: str, image: UploadFile = File(...), metadata: str = Form(...)):
    if not Bridge.has(project_id):
        raise HTTPException(status_code=404, detail={ERROR_KEY: "project id not found"})
    message = EventMsg.loads(metadata)
    image_bytes = await image.read()
    message.id = Bridge.of_id(project_id).save_blob_to_history(
        table_name="image",
        run_id=message.run_id,
        series=message.series,
        meta_data=message.payload,
        timestamp=message.timestamp,
        blob_data=image_bytes,
        num_row_limit=message.history_len,
    )
    message.payload = message.payload or {}
    await Bridge.of_id(project_id).ws_send_to_frontends(message)
    return {RESULT_KEY: "ok", ID_KEY: message.id}


@router.get(f"/{{project_id}}/image/{{image_id}}")
async def get_image_of(project_id: str, image_id: int, meta: Optional[bool] = None):
    if not Bridge.has(project_id):
        raise HTTPException(status_code=404, detail={ERROR_KEY: "project id not found"})
    # Database logic here
    [(_, _, meta_data, image)] = Bridge.of_id(project_id).read_blob_from_history(
        table_name="image", condition=ProjectDbQueryCondition(id=image_id), meta_only=meta
    )
    if meta:
        return Response(meta_data, media_type="application/json")
    else:
        return Response(image, media_type="image/png")


@router.get(f"/{{project_id}}/image")
async def get_history_image_metadata_of(project_id: str, condition: Optional[str] = None):
    if not Bridge.has(project_id):
        raise HTTPException(status_code=404, detail={ERROR_KEY: "project id not found"})
    try:
        condition_json = json.loads(condition) if condition else {}
        condition = ProjectDbQueryCondition.loads(condition_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail={ERROR_KEY: str(e)})
    query_results = Bridge.of_id(project_id).read_blob_from_history(
        table_name="image", condition=condition, meta_only=True
    )
    result = [{"imageId": id, "metadata": meta_data} for (id, _, meta_data) in query_results]
    return result


@router.get(f"/{{project_id}}/scalar")
async def get_history_scalar_of(project_id: str, condition: str = None):
    try:
        condition_json = json.loads(condition) if condition else "{}"
        condition = ProjectDbQueryCondition.loads(condition_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail={ERROR_KEY: str(e)})
    return get_history_json_of(project_id=project_id, table_name="scalar", condition=condition)


@router.get(f"/{{project_id}}/progress")
async def get_history_progress_of(project_id: str, condition: str = None):
    try:
        condition_json = json.loads(condition) if condition else "{}"
        condition = ProjectDbQueryCondition.loads(condition_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail={ERROR_KEY: str(e)})
    return get_history_json_of(project_id=project_id, table_name="progress", condition=condition)
