# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20231204

import logging
import os
import time
from threading import Thread

import werkzeug

werkzeug_log = logging.getLogger("werkzeug")
werkzeug_log.setLevel(logging.ERROR)  # disable flask http call logs
from flask import Response, abort, json, request, send_from_directory

from neetbox.daemon._protocol import *
from neetbox.daemon.server._bridge import Bridge
from neetbox.logging import LogStyle, logger

from .history import *

__PROC_NAME = "NEETBOX SERVER"
logger = logger(__PROC_NAME, LogStyle(skip_writers=["ws"]))


def get_flask_server(debug=False):
    if debug:
        logger.log(f"Running with debug, using APIFlask")
        from apiflask import APIFlask

        app = APIFlask(__PROC_NAME)
    else:
        logger.log(f"Running in production mode, using Flask")
        from flask import Flask

        app = Flask(__PROC_NAME)

    front_end_dist_path = os.path.join(os.path.dirname(__file__), "../../frontend_dist")

    @app.route("/")
    def static_serve_root():
        return send_from_directory(front_end_dist_path, "index.html")

    @app.route("/<path:name>")
    def static_serve(name):
        try:
            return send_from_directory(front_end_dist_path, name)
        except werkzeug.exceptions.NotFound:
            return send_from_directory(front_end_dist_path, "index.html")

    @app.route("/hello", methods=["GET"])
    def just_send_hello():
        return {"hello": "hello"}

    @app.route(f"{FRONTEND_API_ROOT}/list", methods=["GET"])
    def get_list_of_connected_project_ids():
        result = []
        for id, bridge in Bridge.items():
            status = bridge.get_status()
            result.append({"id": id, "online": status["online"], "config": status["config"]})
        return result

    @app.route(f"{FRONTEND_API_ROOT}/log/<project_id>/history", methods=["GET"])
    def get_history_log_of(project_id):
        if not Bridge.has(project_id):
            abort(404)
        _json_data = json.loads(request.args.get("condition"))
        try:
            condition = QueryCondition.from_json(_json_data)
        except Exception as e:  # if failed to parse
            return abort(400)
        result_list = Bridge.of_id(project_id).read_json_from_history(
            table_name="log", condition=condition
        )
        return result_list

    @app.route(f"{FRONTEND_API_ROOT}/status/<project_id>", methods=["GET"])
    def get_status_of(project_id):
        if not Bridge.has(project_id):
            abort(404)
        _returning_stat = Bridge.of_id(project_id).get_status()  # returning specific status
        return _returning_stat

    @app.route(f"{FRONTEND_API_ROOT}/status/<project_id>/history", methods=["GET"])
    def get_history_status_of(project_id):
        if not Bridge.has(project_id):
            abort(404)
        _json_data = json.loads(request.args.get("condition"))
        try:
            condition = QueryCondition.from_json(_json_data)
        except Exception as e:  # if failed to parse
            return abort(400)
        result_list = Bridge.of_id(project_id).read_json_from_history(
            table_name="status", condition=condition
        )
        return result_list

    @app.route(f"{CLIENT_API_ROOT}/sync/<project_id>", methods=["POST"])
    def upload_status_of(project_id):  # client side function
        _json_data = request.get_json()
        target_bridge = Bridge(project_id)  # Create from sync request
        target_bridge.set_status(_json_data)
        return {"result": "ok"}

    @app.route(f"{FRONTEND_API_ROOT}/series/<project_id>/<table_name>", methods=["GET"])
    def get_series_list_of(project_id: str, table_name: str):  # client side function
        if not Bridge.has(project_id):
            abort(404)
        result = Bridge.of_id(project_id).get_series_of(table_name)
        return result

    @app.route(f"{FRONTEND_API_ROOT}/runids/<project_id>", methods=["GET"])
    def get_run_ids_of_projectid(project_id: str):
        if not Bridge.has(project_id):
            abort(404)
        result = Bridge.of_id(project_id).get_run_ids()
        return result

    @app.route(f"/image/<project_id>", methods=["POST"])
    def upload_image(project_id):
        if not Bridge.has(project_id):
            # project id must exist
            # drop anyway if not exist
            if debug:
                logger.log(f"handle log. {project_id} not found.")
            return abort(404)
        _json_data = request.form.to_dict()
        image_bytes = request.files["image"].read()
        lastrowid = Bridge.of_id(project_id).save_blob_to_history(
            table_name="image", meta_data=_json_data, blob_data=image_bytes
        )
        Bridge.of_id(project_id).ws_send_to_frontends(
            json.dumps({"event-type": "image", "imageId": lastrowid, "metadata": _json_data})
        )
        return {"result": "ok", "id": lastrowid}

    @app.route(f"{FRONTEND_API_ROOT}/image/<project_id>/<image_id>", methods=["GET"])
    def get_image_of(project_id, image_id: int):
        if not Bridge.has(project_id):
            return abort(404)  # cannot operate history if bridge of given id not exist
        meta = request.args.get("meta") is not None

        [(_, _, meta_data, image)] = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=QueryCondition(id=image_id), meta_only=meta
        )

        return (
            Response(meta_data, mimetype="application/json")
            if meta
            else Response(image, mimetype="image")
        )

    @app.route(f"{FRONTEND_API_ROOT}/image/<project_id>/history", methods=["GET"])
    def get_history_image_metadata_of(project_id):
        if not Bridge.has(project_id):
            abort(404)
        _json_data = json.loads(request.args.get("condition"))
        try:
            condition = QueryCondition.from_json(_json_data)
        except Exception as e:  # if failed to parse
            return abort(400)
        query_results = Bridge.of_id(project_id).read_blob_from_history(
            table_name="image", condition=condition, meta_only=True
        )  # todo ?
        result = [{"imageId": id, "metadata": meta_data} for id, _, meta_data in query_results]
        return result

    @app.route(f"/shutdown", methods=["POST"])
    def shutdown():
        def __sleep_and_shutdown(secs=1):
            time.sleep(secs)
            os._exit(0)

        Thread(target=__sleep_and_shutdown).start()  # shutdown after 3 seconds
        logger.log(f"BYE.")
        return f"shutdown in 1 seconds."

    return app
