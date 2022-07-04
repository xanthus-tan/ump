# (c) 2021, xanthus tan <tanxk@neusoft.com>
import os
import shutil
from src.ump.modules.release.meta import ReleaseService
from src.ump.modules import ActionBase
from src.ump.msg import SUCCESS, FAILED, WARN
from src.ump.utils import get_unique_id
from src.ump.utils.logger import logger


# release 模块具体实现
class Action(ActionBase):
    def get(self, instruction):
        release_service = ReleaseService()
        release_name = self.name
        rows = release_service.get_release_info(release_name)
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
        file_id = get_unique_id()
        release_service = ReleaseService()
        info = release_service.register_app(file_id=file_id,
                                            release_name=name,
                                            release_tag=tag,
                                            file_size=instruction["size"],
                                            comment=self.comment,
                                            origin_name=instruction["originName"],
                                            origin_suffix=suffix)
        if info == FAILED:
            release_service.close_db_connection()
            logger.error("push failed, Reason: name's tag duplicated")
            self.response.set_display([{"Error": "push failed, Reason: name's tag duplicated"}])
            return FAILED
        release_service.close_db_connection()
        self.response.set_parameter("fileId", file_id)
        self.response.set_display([{"Info": "Waiting push file"}])
        return SUCCESS

    def delete(self, instruction):
        release_tag = instruction["tag"]
        release_name = self.name
        release_service = ReleaseService()
        result = release_service.delete_release(release_name, release_tag)
        release_service.close_db_connection()
        if result <= 0:
            logger.warning("Not found the app.\n\nname:" + release_name + " tag:" + release_tag)
            self.response.set_display([{"Warn": "Not found the app.\n\nname:" + release_name + " tag:" + release_tag}])
            return WARN
        self.response.set_display([{"Info": "Delete success.\n\nname:" + release_name + " tag:" + release_tag}])
        registry_base = self.config.get_registry_path()
        registry = os.path.join(registry_base, release_name, release_tag)
        if os.path.exists(registry):
            shutil.rmtree(registry)
        return SUCCESS
