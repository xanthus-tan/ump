# (c) 2021, xanthus tan <tanxk@neusoft.com>
import os

from sqlalchemy import delete, insert

from src.ump.exector.scheduler import JobDBService
from src.ump.metadata import LINUX_SEP
from src.ump.exector.remote import Connector, RemoteHandler
from src.ump.metadata.module import DeployModule, HostsModule
from src.ump.modules import ActionBase
from src.ump.utils.logger import logger
from src.ump.utils import get_unique_id
from src.ump.msg import SUCCESS, FAILED, WARN
from src.ump.utils.dbutils import DB
from src.ump.modules.instance.model import UmpInstanceInfo

# service模块具体实现
# instance状态
STOP = "stop"
RUN = "running"


class Action(ActionBase):

    def get(self, instruction):
        logger.info("get instance")

    def set(self, instruction):
        if instruction["deploy-name"] is None or instruction["deploy-name"] == "":
            self.response.set_display([{"Warning: ": "deploy name missing"}])
            return WARN
        deploy_name = instruction["deploy-name"]
        dm = DeployModule()
        hosts_info = dm.get_deploy_success_hosts_info(deploy_name)
        db = DB()
        conn = db.get_connect()
        instance_rows = []
        host_rows = []
        host_instance = HostsModule()
        app_absolute_path = ""
        for h in hosts_info:
            host_ip = h["deploy_host"]
            host_group = h["deploy_group"]
            row = {
                "instance_id": get_unique_id(),
                "instance_path": h["app_path"],
                "instance_pid": "-",
                "instance_port": "-",
                "instance_group": host_group,
                "instance_host": host_ip,
                "instance_deploy_name": deploy_name,
                "instance_status": STOP,
            }
            instance_rows.append(row)
            host_info = host_instance.get_host_info(host_group, host_ip)
            host_rows.append(host_info)
            app_absolute_path = h["app_path"]
        if app_absolute_path == "":
            self.response.set_display([{"Error: ": "deploy error, not found app in server"}])
            return FAILED
        with conn.begin():
            s1 = delete(UmpInstanceInfo).where(UmpInstanceInfo.instance_deploy_name == deploy_name)
            conn.execute(s1)
            s2 = insert(UmpInstanceInfo).values(instance_rows)
            conn.execute(s2)
        job_service = JobDBService()
        job_id = job_service.get_job_id_by_target(deploy_name, "deploy")
        if instruction["control"] == "start":
            ssh_conn = Connector()
            pool = ssh_conn.get_ssh_list(host_rows)
            app_dir = os.path.dirname(app_absolute_path)
            log = app_dir + LINUX_SEP + "app.log"
            cmd = "java -jar " + app_absolute_path + " > " + log + " 2>&1 &"
            # cmd = "java -jar " + app_absolute_path
            ssh_handler = RemoteHandler()
            s, f = ssh_handler.remote_shell(pool, cmd)
            print(s)
            logger.info("start app")
        conn.close()

    def delete(self, instruction):
        pass
