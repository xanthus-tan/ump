# (c) 2021, xanthus tan <tanxk@neusoft.com>
import os
import shutil

import sqlalchemy
from sqlalchemy.sql import select, delete, insert

from src.ump.modules import ActionBase
from src.ump.modules.release.model import UmpReleaseInfo
from src.ump.msg import SUCCESS, FAILED, WARN
from src.ump.utils import get_unique_id
from src.ump.utils.dbutils import DB
from src.ump.utils.logger import logger


# release 模块具体实现
class Action(ActionBase):

    def get(self, instruction):
        db = DB()
        conn = db.get_connect()
        if self.name != "":
            s = select(UmpReleaseInfo).where(UmpReleaseInfo.release_name == self.name)
        else:
            s = select(UmpReleaseInfo)
        rs = conn.execute(s)

        rows = []
        for r in rs:
            row = {"name": r.release_name,
                   "tag": r.release_name_tag,
                   "file_size(KB)": r.release_file_size,
                   "origin_name": r.release_origin_name,
                   "type": r.release_origin_suffix,
                   "comment": r.release_comment,
                   "push_time": r.release_push_time.strftime("%Y-%m-%d %H:%M:%S")
                   }
            rows.append(row)
        conn.close()
        self.response.set_display(rows)
        return SUCCESS

    def set(self, instruction):
        registry_base = self.config.get_registry_path()
        name = self.name
        tag = instruction["tag"]
        registry = os.path.join(registry_base, name, tag)
        if not os.path.exists(registry):
            os.makedirs(registry)
        suffix = instruction["originSuffix"]
        db = DB()
        conn = db.get_connect()
        file_id = get_unique_id()
        para = [{"release_file_id": file_id,
                 "release_name": name,
                 "release_file_size": instruction["size"],
                 "release_origin_name": instruction["originName"],
                 "release_origin_suffix": suffix,
                 "release_comment": self.comment,
                 "release_name_tag": tag}]
        s = insert(UmpReleaseInfo).values(para)
        try:
            conn.execute(s)
        except sqlalchemy.exc.IntegrityError as error:
            logger.error(error)
            conn.close()
            self.response.set_display([{"Error": "push failed, Reason: name's tag duplicated"}])
            return FAILED
        conn.close()
        self.response.set_parameter("fileId", file_id)
        self.response.set_display([{"Info": "Waiting push file"}])
        return SUCCESS

    def delete(self, instruction):
        db = DB()
        conn = db.get_connect()
        app_tag = instruction["tag"]
        app_name = self.name
        s = delete(UmpReleaseInfo).where(UmpReleaseInfo.release_name == app_name,
                                         UmpReleaseInfo.release_name_tag == app_tag)
        r = conn.execute(s)
        if r.rowcount <= 0:
            self.response.set_display([{"Warning": "Not found the app.\n\nname:" + app_name + " tag:" + app_tag}])
            return WARN
        self.response.set_display([{"Info": "Delete success.\n\nname:" + app_name + " tag:" + app_tag}])
        registry_base = self.config.get_registry_path()
        registry = os.path.join(registry_base, app_name, app_tag)
        if os.path.exists(registry):
            shutil.rmtree(registry)
        return SUCCESS
