# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240109

import os
import time
from threading import Thread
from typing import Optional, Union

from fastapi import Body, FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, RedirectResponse

import neetbox
from neetbox._protocol import *

from .._bridge import Bridge
from ..db import QueryCondition


def get_fastapi_server(debug=False):
    app = FastAPI()
    from neetbox.logging import LogStyle
    from neetbox.logging.logger import Logger, LogLevel

    logger = Logger("FASTAPI", LogStyle(skip_writers=["ws"]))

    if debug:
        logger.set_log_level(LogLevel.DEBUG)

    front_end_dist_path = os.path.join(os.path.dirname(neetbox.__file__), "frontend_dist")
    logger.info(f"using frontend dist path {front_end_dist_path}")

    # mount web static files root
    app.mount("/static", StaticFiles(directory=front_end_dist_path), name="static")

    @app.get("/")
    def redirect_to_web():
        return RedirectResponse(url="/web/", status_code=301)

    @app.get("/web/{path:path}")
    async def serve_static_root(path: str):
        # Try to return the requested file
        path = "index.html" if not path else path
        static_file_path = f"{front_end_dist_path}/{path}"
        if os.path.isfile(static_file_path):
            return FileResponse(static_file_path)
        else:
            return FileResponse(f"{front_end_dist_path}/index.html")

    @app.get("/hello")
    async def just_send_hello():
        return {"hello": "hello"}

    @app.get(f"{FRONTEND_API_ROOT}/list")
    async def get_status_of_all_proejcts():
        return [_project_status_from_bridge(bridge) for _, bridge in Bridge.items()]

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}")
    async def get_status_of_project_id(project_id: str):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
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
            "online": bridge.is_online(),
            NAME_KEY: name_of_project,
            "runids": run_id_info_list,
        }

    def get_history_json_of(project_id: str, table_name: str, condition=Union[dict, str]):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            raise HTTPException(status_code=404, detail={ERROR_KEY: "Project ID not found"})
        try:
            if isinstance(condition, str):
                condition = json.loads(condition)
            if isinstance(condition, dict):
                condition = QueryCondition.from_json(condition)
        except Exception as e:  # if failed to parse
            error_message = f"failed to parse condition from {type(condition)}{condition} :{e}"
            logger.debug(error_message, prefix="400")
            raise HTTPException(status_code=400, detail={ERROR_KEY: error_message})
        return Bridge.of_id(project_id).read_json_from_history(
            table_name=table_name, condition=condition
        )

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/log")
    async def get_history_log_of(project_id: str, condition: str):
        return get_history_json_of(
            project_id=project_id,
            table_name=LOG_TABLE_NAME,
            condition=condition,
        )

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/hardware")
    async def get_history_hardware_info_of(project_id: str, condition: str):
        return get_history_json_of(
            project_id=project_id,
            table_name=EVENT_TYPE_NAME_HARDWARE,
            condition=condition,
        )

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/series/{{table_name}}")
    async def get_series_list_of(
        project_id: str, table_name: str, run_id: str = None
    ):  # client side function
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            raise HTTPException(status_code=404, detail={ERROR_KEY: "Project ID not found"})
        result = Bridge.of_id(project_id).get_series_of(table_name, run_id=run_id)
        return result

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/run/{{run_id}}")
    async def get_status_of(project_id, run_id):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            raise HTTPException(status_code=404, detail={ERROR_KEY: "Project ID not found"})
        result = Bridge.of_id(project_id).get_status(run_id=run_id)
        return result

    @app.put(f"{FRONTEND_API_ROOT}/project/{{project_id}}/run/{{run_id}}")
    async def set_get_metadata_of_run_id(project_id: str, run_id: str, metadata: dict = Body(...)):
        bridge = Bridge.of_id(project_id)
        try:
            old_metadata = bridge.historyDB.fetch_metadata_of_run_id(
                run_id=run_id
            )  # get old metadata
            old_metadata.update(metadata)
            # Assuming the method to update metadata in your database might look like this
            bridge.historyDB.update_metadata_of_run_id(run_id=run_id, metadata=old_metadata)
            return bridge.historyDB.fetch_metadata_of_run_id(run_id=run_id)
        except Exception as e:  # Replace with your specific database exception
            raise HTTPException(status_code=404, detail={ERROR_KEY: str(e)})

    @app.delete(f"{FRONTEND_API_ROOT}/project/{{project_id}}/run/{{run_id}}")
    async def delete_run_id(project_id: str, run_id: str):
        bridge = Bridge.of_id(project_id)
        if bridge.is_online(run_id):  # cannot delete running projects
            raise HTTPException(
                status_code=400, detail={ERROR_KEY: "can only delete history run id."}
            )
        bridge.historyDB.delete_run_id(run_id)
        if 0 == len(bridge.get_run_ids()):  # check if all the run ids are deleted
            del Bridge._id2bridge[project_id]  # delete the empty bridge
        return {RESULT_KEY: "success"}

    @app.post("/image/{project_id}")
    async def upload_image(
        project_id: str, image: UploadFile = File(...), metadata: str = Form(...)
    ):
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
        Bridge.of_id(project_id).ws_send_to_frontends(message)
        return {"result": "ok", "id": message.id}

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/image/{{image_id}}")
    async def get_image_of(project_id: str, image_id: int, meta: Optional[bool] = None):
        if not Bridge.has(project_id):
            raise HTTPException(status_code=404, detail={ERROR_KEY: "project id not found"})
        # Database logic here
        [(_, _, meta_data, image)] = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=QueryCondition(id=image_id), meta_only=meta
        )
        if meta:
            return Response(meta_data, media_type="application/json")
        else:
            return Response(image, media_type="image/png")

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/image")
    async def get_history_image_metadata_of(project_id: str, condition: Optional[str] = None):
        if not Bridge.has(project_id):
            raise HTTPException(status_code=404, detail={ERROR_KEY: "project id not found"})

        try:
            condition_json = json.loads(condition) if condition else {}
            condition = QueryCondition.from_json(condition_json)
        except Exception as e:
            raise HTTPException(status_code=400, detail={ERROR_KEY: str(e)})

        query_results = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=condition, meta_only=True
        )
        result = [{"imageId": id, "metadata": meta_data} for (id, _, meta_data) in query_results]
        return result

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/scalar")
    async def get_history_scalar_of(project_id: str, condition: str = None):
        try:
            condition_json = json.loads(condition) if condition else "{}"
            condition = QueryCondition.from_json(condition_json)
        except Exception as e:
            raise HTTPException(status_code=400, detail={ERROR_KEY: str(e)})
        return get_history_json_of(project_id=project_id, table_name="scalar", condition=condition)

    @app.get(f"{FRONTEND_API_ROOT}/project/{{project_id}}/progress")
    async def get_history_progress_of(project_id: str, condition: str = None):
        try:
            condition_json = json.loads(condition) if condition else "{}"
            condition = QueryCondition.from_json(condition_json)
        except Exception as e:
            raise HTTPException(status_code=400, detail={ERROR_KEY: str(e)})
        return get_history_json_of(
            project_id=project_id, table_name="progress", condition=condition
        )

    @app.post(f"/shutdown")
    async def shutdown():
        def __sleep_and_shutdown(secs=1):
            time.sleep(secs)
            os._exit(0)

        Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
        logger.log(f"BYE.")
        return {RESULT_KEY: f"shutdown in 1 seconds."}

    return app
