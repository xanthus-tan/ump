# (c) 2021, xanthus tan <tanxk@neusoft.com>
import os

from src.ump.exector.remote import Connector, RemoteHandler
from src.ump.utils import LINUX_SEP
from src.ump.metadata.module import DeployModule, HostsModule
from src.ump.modules import ActionBase
from src.ump.msg import SUCCESS, FAILED, WARN
from src.ump.utils.logger import logger


# instance模块具体实现
class Action(ActionBase):

    def get(self, instruction):
        deploy_name = instruction["deploy-name"]
        deploy_module = DeployModule()
        info = deploy_module.get_deploy_success_hosts_info(deploy_name)
        self.response.set_display(info)
        return SUCCESS

    def set(self, instruction):
        deploy_name = instruction["deploy-name"]
        if deploy_name is None or deploy_name == "":
            self.response.set_display([{"Warning: ": "deploy name missing"}])
            return WARN
        ctl = instruction["control"]
        if ctl is None or ctl == "":
            self.response.set_display([{"Warn: ": "control parameter　not found"}])
            return WARN
        instance_id = instruction["insid"]
        ctl = instruction["control"]
        dm = DeployModule()
        deploy = dm.get_current_deploy_info(deploy_name)
        deploy_path = deploy["deploy_path"]
        startup_args = deploy["deploy_startup_args"]
        if instance_id is None or instance_id == "":
            if ctl == "start":
                started_instances = dm.get_started_instance_info(deploy_name)
                group_name = dm.get_deploy_group(deploy_name)
                ssh_conn = Connector()
                ssh_pool = ssh_conn.get_ssh_pool(group_name)
                s, f = _start_instance(ssh_pool, deploy_path, startup_args)
                if len(f) == len(ssh_pool):
                    self.response.set_display([{"failure": "start instance failure, could not connect to host"}])
                    return FAILED
                logger.info("start instance all")
                if len(started_instances) > 0:
                    msg = ""
                    for si in started_instances:
                        msg = msg + si["instance_id"] + "\n"
                    self.response.set_display([{"WARN": "Repeat the boot instance " + "\n" + msg}])
                    return WARN
                self.response.set_display([{"Info: ": deploy_name + " instance all started"}])
                return SUCCESS
            elif ctl == "stop":
                hm = HostsModule()
                ssh_conn = Connector()
                started_instances = dm.get_started_instance_info(deploy_name)
                # 轮询关闭实例进程
                for instance in started_instances:
                    sid = instance["instance_id"]
                    gh = dm.get_instance_group_and_host(sid)
                    if gh is None:
                        continue
                    host = hm.get_host_info(gh["group"], gh["host"])
                    l = [host]
                    pool = ssh_conn.get_ssh_pool_by_hosts(l)
                    pid = instance["instance_pid"]
                    _stop_instance(pool, pid)
                logger.info("stop instance all")
            else:
                logger.warning("control cmd " + ctl + " not found")
        else:
            if ctl == "start":
                gh = dm.get_instance_group_and_host(instance_id)
                if gh is None:
                    self.response.set_display([{"WARN: ": "not found instance"}])
                    return WARN
                ins_pid = dm.get_instance_pid(instance_id)
                if ins_pid is not None:
                    self.response.set_display([{"WARN: ": "The instnace pid exist, can't start"}])
                    return WARN
                hm = HostsModule()
                host = hm.get_host_info(gh["group"], gh["host"])
                l = [host]
                ssh_conn = Connector()
                pool = ssh_conn.get_ssh_pool_by_hosts(l)
                s, f = _start_instance(pool, deploy_path, startup_args)
                if len(f) > 0:
                    self.response.set_display([{"failure": "start instance failure, could not connect to host"}])
                    return FAILED
                logger.info("start instance + " + instance_id)
                self.response.set_display([{"Info: ": "instance " + instance_id + " started"}])
                return SUCCESS
            elif ctl == "stop":
                gh = dm.get_instance_group_and_host(instance_id)
                if gh is None:
                    self.response.set_display([{"WARN: ": "not found instance"}])
                    return WARN
                hm = HostsModule()
                host = hm.get_host_info(gh["group"], gh["host"])
                l = [host]
                ssh_conn = Connector()
                pool = ssh_conn.get_ssh_pool_by_hosts(l)
                instance_pid = dm.get_instance_pid(instance_id)
                if instance_pid is None:
                    self.response.set_display([{"WARN: ": "The instance not found pid, may be have been stopped"}])
                    return WARN
                s, f = _stop_instance(pool, instance_pid)
                if len(f) > 0:
                    self.response.set_display([{"failure": "stop instance failure, could not connect to host"}])
                    return FAILED
                logger.info("stop instance + " + instance_id)
            else:
                logger.warning("control cmd " + ctl + " not found")

    def delete(self, instruction):
        pass


def _start_instance(pool, path, args):
    app_dir = os.path.dirname(path)
    log = app_dir + LINUX_SEP + "app.log"
    if args is None:
        start_cmd = "java -jar " + path + " > " + log + " 2>&1 &"
    else:
        start_cmd = "java -jar " + path + " " + args + " > " + log + " 2>&1 &"
    logger.debug("command is :" + start_cmd)
    ssh_handler = RemoteHandler()
    s, f = ssh_handler.remote_shell(pool, start_cmd)
    return s, f


def _stop_instance(pool, pid):
    stop_cmd = "kill -9 " + str(pid)
    ssh_handler = RemoteHandler()
    s, f = ssh_handler.remote_shell(pool, stop_cmd)
    logger.debug("command is :" + stop_cmd)
    return s, f
