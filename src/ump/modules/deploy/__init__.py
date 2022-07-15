# (c) 2021, xanthus tan <tanxk@neusoft.com>

import os
from os.path import basename
from src.ump.modules.deploy.meta import DeployService, INSTANCE_STOP, INSTANCE_START, get_instance_health_check_cache
from src.ump.exector.scheduler import JobDBService, UmpJob, Job
from src.ump.metadata import LINUX_SEP
from src.ump.exector.remote import Connector, RemoteHandler
from src.ump.msg import SUCCESS, FAILED, WARN
# fix Circular Import Error
import src.ump.metadata.module as module
from src.ump.modules import ActionBase
from src.ump.utils.logger import logger
from src.ump.utils import get_current_local_datetime, get_unique_id


# deploy模块具体实现
class Action(ActionBase, UmpJob):
    # 服务启动时, 该模块job自动加载
    def job_boot(self, **args):
        deploy_name = args["job_name"]
        job_id = args["job_id"]
        job_interval = args["job_interval"]
        ssh_timeout = int(args["job_ssh_timeout"])
        ds = DeployService()
        deploy_info = ds.get_deploy_info(deploy_name)
        if deploy_info is None:
            return None
        deploy_obj = deploy_info[0]
        instances = ds.get_deploy_instance_info(deploy_name)
        ihc = get_instance_health_check_cache()
        ihc[deploy_name] = {}
        for instance in instances:
            ihc[deploy_name][instance["instance_host"]] = {
                "instance_id": instance["instance_id"],
                "instance_status": instance["instance_status"]
            }
        job = Job()
        job.set_job_id(job_id)
        job.set_job_interval(job_interval)
        ssh_conn = Connector()
        group_name = deploy_obj["deploy_group"]
        file_name = deploy_obj["deploy_path"]
        ssh_conn_poll = ssh_conn.get_ssh_pool(group_name)
        job.set_job_func(_health_check, [ssh_conn_poll, ssh_timeout, basename(file_name), deploy_name])
        job.job_start()
        logger.info("start health check")
        ds.close_db_connection()

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
        deploy_service = DeployService()
        instances = deploy_service.get_deploy_instance_info(deploy_name)
        for ins in instances:
            status = ins["instance_status"]
            if status == INSTANCE_START:
                self.response.set_display([{"WARN": "The instnace is alive, the first close instnace."}])
                return WARN
        release_file_id = meta.get_file_id()
        registry_path = self.config.get_registry_path()
        src_target = os.path.join(registry_path, app_name, app_tag, release_file_id)
        file_suffix = meta.get_file_suffix()
        target_file_id = get_unique_id()
        if deploy_home is None or deploy_home == "":
            self.response.set_display([{"Error": "Missing dest parameter"}])
            return FAILED
        if deploy_home[-1] != LINUX_SEP:
            deploy_home = deploy_home + LINUX_SEP
        prev_deploy_app = ""
        prev_deploy_id = ""
        # 获取当前部署状态
        deploy_info = deploy_service.get_current_deploy_id_and_app_name(deploy_name)
        if deploy_info is not None:
            prev_deploy_app = deploy_info["deploy_app"]
            prev_deploy_id = deploy_info["deploy_id"]
            if prev_deploy_app == app:
                self.response.set_display([{"WARN": app + " has been deployed"}])
                return WARN
        ssh_conn = Connector()
        ssh_conn_poll = ssh_conn.get_ssh_pool(self.group)
        parent_dir = deploy_home + self.config.get_root_dir_name()
        deploy_path = parent_dir + LINUX_SEP + deploy_name + LINUX_SEP + app_tag
        ssh_timeout = self.config.get_ssh_timeout()
        rh = RemoteHandler(ssh_timeout)
        rh.remote_shell(ssh_conn_poll, "mkdir -p " + deploy_path)
        target_file = target_file_id + "." + file_suffix
        deploy_target = deploy_path + LINUX_SEP + target_file
        success_hosts, failure_hosts = rh.remote_copy(ssh_conn_poll, src_target, deploy_target)
        if len(failure_hosts) == len(ssh_conn_poll):
            self.response.set_display([{"Error": "Deploy failure"}])
            return FAILED
        instance_rows = deploy_service.create_new_deploy(prev_deploy_id=prev_deploy_id,
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
        # 开启健康检测,默认开启
        if instruction["health"]:
            interval = self.config.get_health_interval()
            job_service.save_job(deploy_name, "deploy", interval, ssh_timeout)
            ihc = get_instance_health_check_cache()
            ihc[deploy_name] = {}
            for instance in instance_rows:
                ihc[deploy_name][instance["instance_host"]] = {
                    "instance_id": instance["instance_id"],
                    "instance_status": instance["instance_status"]
                }
            job_service.job_begin(callback=_health_check, args=[ssh_conn_poll, ssh_timeout, target_file, deploy_name])
            logger.info("start health check")
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
            self.response.set_display([{"Warn": "Missing name parameter"}])
            return WARN
        deploy_service = DeployService()
        instances = deploy_service.get_deploy_instance_info(deploy_name)
        for ins in instances:
            status = ins["instance_status"]
            if status == INSTANCE_START:
                self.response.set_display([{"WARN": "The first close all instances otherwise it cannot be deleted"}])
                return WARN
        result = deploy_service.delete_deploy(deploy_name)
        if result is None:
            self.response.set_display([{"Warn": "Not found " + deploy_name}])
            return WARN
        deploy_service.close_db_connection()
        job_service = JobDBService()
        job_service.delete_job_by_target(deploy_name, "deploy")
        job_service.close_job_db_connection()
        self.response.set_display([{"Info": deploy_name + " has been deleted"}])
        return SUCCESS


def _health_check(ssh_pool, ssh_timeout, clue, deploy_name):
    rh = RemoteHandler(ssh_timeout)
    success, failure = rh.remote_shell(ssh_pool, "jps | grep " + clue)
    ds = DeployService()
    ihc = get_instance_health_check_cache()
    current_deploy_check_cache = ihc[deploy_name]
    for m in success:
        out = m["out"]
        host = m["host"]
        status = current_deploy_check_cache[host]["instance_status"]
        sid = current_deploy_check_cache[host]["instance_id"]
        if out is None or out == "":
            if status == INSTANCE_STOP:
                continue
            else:
                # 更新缓存内存
                current_deploy_check_cache[host]["instance_status"] = INSTANCE_STOP
                ds.update_instance(sid, None, INSTANCE_STOP, stop_time=get_current_local_datetime())
        else:
            if status == INSTANCE_START:
                continue
            else:
                current_deploy_check_cache[host]["instance_status"] = INSTANCE_START
                pid = out.split()[0]
                ds.update_instance(sid, pid, INSTANCE_START, start_time=get_current_local_datetime())
    ds.close_db_connection()
    logger.debug(ihc)
