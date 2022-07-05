# (c) 2021, xanthus tan <tanxk@neusoft.com>

import os
from src.ump.modules.deploy.meta import DeployService
from src.ump.exector.scheduler import JobDBService
from src.ump.metadata import LINUX_SEP
from src.ump.exector.remote import Connector, RemoteHandler
from src.ump.msg import SUCCESS, FAILED, WARN
# fix Circular Import Error
import src.ump.metadata.module as module
from src.ump.modules import ActionBase
from src.ump.utils.logger import logger


# deploy模块具体实现
class Action(ActionBase):
    def get(self, instruction):
        deploy_name = self.name
        if deploy_name == "":
            self.response.set_display([{"Error": "name value is missing!"}])
            return WARN
        deploy_service = DeployService()
        if instruction["detail"]:
            instance_info_rows = deploy_service.get_deploy_instance_info(deploy_name)
            self.response.set_display(instance_info_rows)
            return SUCCESS
        history = instruction["history"]
        deploy_service = DeployService()
        rows = deploy_service.get_deploy_info(deploy_name, history=history)
        if rows is None:
            return SUCCESS
        self.response.set_display(rows)
        deploy_service.close_db_connection()
        return SUCCESS

    def set(self, instruction):
        app = instruction["app"]
        app_name = app.split(":")[0]
        app_tag = app.split(":")[1]
        deploy_home = instruction["dest"]
        deploy_name = self.name
        try:
            meta = module.ReleaseModule(app_name, app_tag)
        except AttributeError as error:
            logger.error(error)
            logger.error("Not found app in register")
            self.response.set_display([{"Error": "Not found app in register"}])
            return FAILED
        file_id = meta.get_file_id()
        registry_path = self.config.get_registry_path()
        src_target = os.path.join(registry_path, app_name, app_tag, file_id)
        file_suffix = meta.get_file_suffix()
        file = file_id + "." + file_suffix
        if deploy_home is None or deploy_home == "":
            self.response.set_display([{"Error": "Missing dest parameter"}])
            return FAILED
        if deploy_home[-1] != LINUX_SEP:
            deploy_home = deploy_home + LINUX_SEP
        prev_deploy_app = ""
        prev_deploy_id = ""
        deploy_service = DeployService()
        # 获取当前部署状态
        deploy_info = deploy_service.get_current_deploy_id_and_app(deploy_name)
        if deploy_info is not None:
            prev_deploy_app = deploy_info["deploy_app"]
            prev_deploy_id = deploy_info["deploy_id"]
            if prev_deploy_app == app:
                self.response.set_display([{"WARN": app + " has been deployed"}])
                return WARN
        c1 = Connector()
        ssh_pool = c1.get_ssh_pool(self.group)
        handler = RemoteHandler(self.config.get_ssh_timeout())
        parent_dir = deploy_home + self.config.get_root_dir_name()
        deploy_path = parent_dir + LINUX_SEP + deploy_name + LINUX_SEP + app_tag
        handler.remote_shell(ssh_pool, "mkdir -p " + deploy_path)
        c1.close_ssh_connect()
        c2 = Connector()
        ssh_pool = c2.get_ssh_pool(self.group)
        deploy_target = deploy_path + LINUX_SEP + file
        success_hosts, failure_hosts = handler.remote_copy(ssh_pool, src_target, deploy_target)
        c2.close_ssh_connect()
        host_num = len(ssh_pool)
        if len(failure_hosts) == host_num:
            self.response.set_display([{"Error": "Deploy failure"}])
            return FAILED
        deploy_service.create_new_deploy(prev_deploy_id=prev_deploy_id,
                                         prev_deploy_app=prev_deploy_app,
                                         deploy_group=self.group,
                                         deploy_name=deploy_name,
                                         deploy_path=deploy_target,
                                         deploy_app=app,
                                         success_hosts=success_hosts,
                                         failure_hosts=failure_hosts,
                                         deploy_comment=self.comment)
        deploy_service.close_db_connection()
        # 清空上一次健康检测任务
        job_service = JobDBService()
        job_service.delete_job_by_target(deploy_name, "deploy")
        # 开启健康检测
        if instruction["health"]:
            job_id = job_service.save_job(deploy_name, "deploy")
        job_service.close_job_db_connection()
        # end
        rows = []
        if len(failure_hosts) != 0:
            for h in failure_hosts:
                row = {
                    "failed host": h
                }
                rows.append(row)
            self.response.set_display(rows)
            return WARN
        self.response.set_display([{"Info": "The app deploy success"}])
        return SUCCESS

    def delete(self, instruction):
        deploy_name = self.name
        if deploy_name == "":
            self.response.set_display([{"Warn": "name value is missing!"}])
            return WARN
        deploy_service = DeployService()
        result = deploy_service.delete_deploy(deploy_name)
        if result is None:
            self.response.set_display([{"Warn": "Not found " + deploy_name}])
            return WARN
        deploy_service.close_db_connection()
        self.response.set_display([{"Info": deploy_name + " has been deleted"}])
        return SUCCESS
