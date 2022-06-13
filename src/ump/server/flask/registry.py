# (c) 2021, xanthus tan <tanxk@neusoft.com>
import os

from flask import Flask, make_response
from flask import request

from src.ump.utils.logger import logger

registry_app = Flask(__name__)


@registry_app.route("/", methods=["POST", "GET"])
def hello_world():
    print(registry_app.registry_base)
    return "<p>This is a ump registry server!</p>"


@registry_app.route("/registry/push", methods=["POST"])
def push():
    if 'file' not in request.files:
        msg = "Registry Server: push failed"
        return make_response(msg, 500)
    file = request.files["file"]
    app_id = request.form.get("fileId")
    app_name = request.form.get("appName")
    app_tag = request.form.get("appTag")
    dst = os.path.join(registry_app.registry_base, app_name, app_tag, app_id)
    file.save(dst)
    logger.info("push file success")
    msg = "Registry Server: push success"
    return msg
