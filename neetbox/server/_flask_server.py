# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231204

import logging
import os
import time
from threading import Thread
from typing import Union

import werkzeug
from flask import Response, abort, json, redirect, request, send_from_directory

import neetbox
from neetbox._protocol import *
from neetbox.server._bridge import Bridge

from .db import QueryCondition

werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.ERROR)  # disable flask http call logs


def get_flask_server(debug=False):
    __PROC_NAME = "NEETBOX"
    from neetbox.logging import LogStyle
    from neetbox.logging.logger import Logger, LogLevel

    logger = Logger("NEETBOX", LogStyle(skip_writers=["ws"]))

    if debug:
        logger.set_log_level(LogLevel.DEBUG)
        logger.log(f"Running with debug, using APIFlask")
        from apiflask import APIFlask

        app = APIFlask(__PROC_NAME, static_folder=None)
    else:
        logger.log(f"Running in production mode, using Flask")
        from flask import Flask

        app = Flask(__PROC_NAME, static_folder=None)

    front_end_dist_path = os.path.join(os.path.dirname(neetbox.__file__), "frontend_dist")

    @app.route("/")
    def static_serve_root():
        return redirect("/web/")

    @app.route("/web/")
    @app.route("/web/<path:name>")
    def static_serve(name=""):
        try:
            return send_from_directory(front_end_dist_path, name)
        except werkzeug.exceptions.NotFound:
            return send_from_directory(front_end_dist_path, "index.html")

    @app.route("/hello", methods=["GET"])
    def just_send_hello():
        return {"hello": "hello"}

    @app.route(f"{FRONTEND_API_ROOT}/list", methods=["GET"])
    def get_status_of_all_proejcts():
        return [_project_status_from_bridge(bridge) for _, bridge in Bridge.items()]

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>", methods=["GET"])
    def get_status_of_project_id(project_id: str):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            abort(404, {ERROR_KEY: "project id not found"})
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
            abort(404, {ERROR_KEY: "project id not found"})
        try:
            condition = QueryCondition.from_json(
                json.loads(condition) if isinstance(condition, str) else condition
            )
        except Exception as e:  # if failed to parse
            logger.debug(f"failed to parse condition string", prefix="400")
            abort(400, {ERROR_KEY: "failed to parse condition string"})
        return Bridge.of_id(project_id).read_json_from_history(
            table_name=table_name, condition=condition
        )

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/log", methods=["GET"])
    def get_history_log_of(project_id):
        return get_history_json_of(
            project_id=project_id,
            table_name=LOG_TABLE_NAME,
            condition=request.args.get("condition"),
        )

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/hardware", methods=["GET"])
    def get_history_hardware_of(project_id):
        return get_history_json_of(
            project_id=project_id,
            table_name=EVENT_TYPE_NAME_HARDWARE,
            condition=request.args.get("condition"),
        )

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/series/<table_name>", methods=["GET"])
    def get_series_list_of(project_id: str, table_name: str):  # client side function
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            abort(404, {ERROR_KEY: "project id not found"})
        result = Bridge.of_id(project_id).get_series_of(
            table_name, run_id=request.args.get(RUN_ID_KEY)
        )
        return result

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/run/<run_id>", methods=["GET"])
    def get_status_of(project_id, run_id):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            abort(404, {ERROR_KEY: "project id not found"})
        result = Bridge.of_id(project_id).get_status(run_id=run_id)
        return result

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/run/<run_id>", methods=["PUT"])
    def set_get_metadata_of_run_id(project_id: str, run_id: str):
        new_metadata = request.json
        bridge = Bridge.of_id(project_id)
        old_metadata = bridge.historyDB.fetch_metadata_of_run_id(run_id=run_id)  # get old metadata
        for k, v in new_metadata.items():
            old_metadata[k] = v
        return bridge.historyDB.fetch_metadata_of_run_id(run_id=run_id, metadata=new_metadata)

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/run/<run_id>", methods=["DELETE"])
    def delete_run_id(project_id: str, run_id: str):
        bridge = Bridge.of_id(project_id)
        if bridge.is_online(run_id):  # cannot delete running projects
            abort(400, {ERROR_KEY: "can only delete history run id."})
        bridge.historyDB.delete_run_id(run_id)
        if 0 == len(bridge.get_run_ids()):  # check if all the run ids are deleted
            del Bridge._id2bridge[project_id]  # delete the empty bridge
        return {RESULT_KEY: "success"}

    @app.route(f"/image/<project_id>", methods=["POST"])
    def upload_image(project_id):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            abort(404, {ERROR_KEY: "project id not found"})
        message = EventMsg.loads(request.form["json"])
        image_bytes = request.files["image"].read()
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

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/image/<image_id>", methods=["GET"])
    def get_image_of(project_id, image_id: int):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            abort(404, {ERROR_KEY: "project id not found"})
        meta = request.args.get("meta") is not None

        [(_, _, meta_data, image)] = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=QueryCondition(id=image_id), meta_only=meta
        )

        return (
            Response(meta_data, mimetype="application/json")
            if meta
            else Response(image, mimetype="image")
        )

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/image", methods=["GET"])
    def get_history_image_metadata_of(project_id):
        if not Bridge.has(project_id):
            logger.debug(f"visiting none existing project id {project_id}", prefix="[404]")
            abort(404, {ERROR_KEY: "project id not found"})
        _json_data = json.loads(request.args.get("condition", default="{}"))
        try:
            condition = QueryCondition.from_json(_json_data)
        except Exception as e:  # if failed to parse
            return abort(400)
        query_results = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=condition, meta_only=True
        )  # todo ?
        result = [{"imageId": id, "metadata": meta_data} for id, _, meta_data in query_results]
        return result

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/scalar", methods=["GET"])
    def get_history_scalar_of(project_id):
        return get_history_json_of(
            project_id=project_id, table_name="scalar", condition=request.args.get("condition")
        )

    @app.route(f"{FRONTEND_API_ROOT}/project/<project_id>/progress", methods=["GET"])
    def get_history_progress_of(project_id):
        return get_history_json_of(
            project_id=project_id, table_name="progress", condition=request.args.get("condition")
        )

    @app.route(f"/shutdown", methods=["POST"])
    def shutdown():
        def __sleep_and_shutdown(secs=1):
            time.sleep(secs)
            os._exit(0)

        Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
        logger.log(f"BYE.")
        return {RESULT_KEY: f"shutdown in 1 seconds."}

    return app
