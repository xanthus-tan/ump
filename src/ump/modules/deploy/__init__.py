# (c) 2021, xanthus tan <tanxk@neusoft.com>

import os

from sqlalchemy import select, insert, update, delete

from exector.remote import Connector, RemoteHandler
from modules.deploy.model import UmpDeployInfo, UmpDeployDetailInfo
from msg import SUCCESS, FAILED, WARN
from src.ump.metadata.meta import ReleaseMeta
from src.ump.modules import ActionBase
from src.ump.utils.logger import logger
from utils.dbutils import DB

CURRENT = "current"
COMPLETED = "completed"


# deploy模块具体实现
class Action(ActionBase):
    def get(self, instruction):
        deploy_name = self.name
        if deploy_name == "":
            self.response.set_display([{"Error": "name value is missing!"}])
            return WARN
        db = DB()
        conn = db.get_connect()
        rows = []
        if instruction["detail"]:
            detail = select(UmpDeployDetailInfo).where(UmpDeployDetailInfo.deploy_name == deploy_name)
            rs = conn.execute(detail)
            for r in rs:
                row = {
                    "deploy_name": r.deploy_name,
                    "deploy_host": r.deploy_host,
                    "deploy_status": r.deploy_status,
                    "deploy_date": r.deploy_time.strftime("%Y-%m-%d %H:%M:%S")
                }
                rows.append(row)
            self.response.set_display(rows)
            conn.close()
            return SUCCESS
        if instruction["history"]:
            s = select(UmpDeployInfo).where(UmpDeployInfo.deploy_name == deploy_name)
        else:
            s = select(UmpDeployInfo).where(UmpDeployInfo.deploy_status == CURRENT,
                                            UmpDeployInfo.deploy_name == deploy_name)
        rs = conn.execute(s)
        for r in rs:
            row = {
                "deploy_name": r.deploy_name,
                "deploy_path": r.deploy_path,
                "deploy_app": r.deploy_app,
                "deploy_app_last": r.deploy_app_last,
                "deploy_group": r.deploy_group,
                "host_num": r.deploy_host_num,
                "failed_num": r.deploy_failed_num,
                "deploy_status": r.deploy_status,
                "deploy_date": r.deploy_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            rows.append(row)
        self.response.set_display(rows)
        conn.close()
        return SUCCESS

    def set(self, instruction):
        app = instruction["app"]
        app_name = app.split(":")[0]
        app_tag = app.split(":")[1]
        deploy_home = instruction["dest"]
        deploy_name = self.name
        try:
            meta = ReleaseMeta(app_name, app_tag)
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
        # Linux 分隔符
        linux_sep = "/"
        if deploy_home is None or deploy_home == "":
            self.response.set_display([{"Info": "Missing dest parameter"}])
            return FAILED
        if deploy_home[-1] != linux_sep:
            deploy_home = deploy_home + linux_sep
        # deploy_target = deploy_home + deploy_name + linux_sep + app_tag + linux_sep + file
        # 登记部署信息
        db = DB()
        conn = db.get_connect()
        # 获取当前部署状态
        s = select(UmpDeployInfo).\
            where(UmpDeployInfo.deploy_status == CURRENT,
                  UmpDeployInfo.deploy_name == self.name)
        rs = conn.execute(s).fetchone()
        deploy_app_last = ""
        deploy_app_id_last = ""
        if rs is not None:
            deploy_app_last = rs._mapping["deploy_app"]
            deploy_app_id_last = rs._mapping["id"]
            if deploy_app_last == app:
                self.response.set_display([{"Info": "The app has been deployed"}])
                return SUCCESS
        c1 = Connector()
        ssh_pool = c1.get_ssh_pool(self.group)
        handler = RemoteHandler(self.config.get_ssh_timeout())
        deploy_path = deploy_home + deploy_name + linux_sep + app_tag
        handler.remote_shell(ssh_pool, "mkdir -p " + deploy_path)
        c1.close_ssh_connect()
        c2 = Connector()
        ssh_pool = c2.get_ssh_pool(self.group)
        deploy_target = deploy_path + linux_sep + file
        success_hosts, failed_hosts = handler.remote_copy(ssh_pool, src_target, deploy_target)
        c2.close_ssh_connect()
        host_num = len(ssh_pool)
        failed_num = len(failed_hosts)
        if failed_num == host_num:
            self.response.set_display([{"Error": "Deploy failed"}])
            return FAILED
        # 开启事务
        with conn.begin():
            # 将当前部署状态归档
            s1 = update(UmpDeployInfo).\
                where(UmpDeployInfo.id == deploy_app_id_last).\
                values({"deploy_status": COMPLETED})
            conn.execute(s1)
            deploy_info = {
                "deploy_name": self.name,
                "deploy_path": deploy_target,
                "deploy_app": instruction["app"],
                "deploy_group": self.group,
                "deploy_app_last": deploy_app_last,
                "deploy_comment": self.comment,
                "deploy_host_num": host_num,
                "deploy_failed_num": failed_num
            }
            # 更新最新部署状态
            s2 = insert(UmpDeployInfo).values(deploy_info)
            conn.execute(s2)
            # 删除部署细节信息
            s3 = delete(UmpDeployDetailInfo).where(UmpDeployDetailInfo.deploy_name == self.name)
            conn.execute(s3)
            detail_rows = []
            for f in failed_hosts:
                v = {
                    "deploy_name": self.name,
                    "deploy_host": f,
                    "deploy_status": "failed"
                }
                detail_rows.append(v)
            for f in success_hosts:
                v = {
                    "deploy_name": self.name,
                    "deploy_host": f,
                    "deploy_status": "success"
                }
                detail_rows.append(v)
            # 更新最新部署细节信息
            s4 = insert(UmpDeployDetailInfo).values(detail_rows)
            conn.execute(s4)
        conn.close()
        # end
        rows = []
        if len(failed_hosts) != 0:
            for h in failed_hosts:
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
            self.response.set_display([{"Warning": "name value is missing!"}])
            return WARN
        db = DB()
        conn = db.get_connect()
        s = select(UmpDeployInfo).\
            where(UmpDeployInfo.deploy_status == CURRENT,
                  UmpDeployInfo.deploy_name == self.name)
        rs = conn.execute(s).fetchone()
        if rs is None:
            self.response.set_display([{"Warning": "Not found " + deploy_name}])
            return WARN
        with conn.begin():
            if instruction["history"]:
                s1 = delete(UmpDeployInfo).\
                    where(UmpDeployInfo.deploy_name == deploy_name,
                          UmpDeployInfo.deploy_status == COMPLETED)
            else:
                s1 = delete(UmpDeployInfo).where(UmpDeployInfo.deploy_name == deploy_name)

            s2 = delete(UmpDeployDetailInfo).where(UmpDeployDetailInfo.deploy_name == deploy_name)
            c1 = conn.execute(s1)
            print(c1.rowcount)
            c2 = conn.execute(s2)
        conn.close()
        self.response.set_display([{"Info": deploy_name + " has been deleted"}])
        return SUCCESS



