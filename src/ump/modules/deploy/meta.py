# (c) 2021, xanthus tan <tanxk@neusoft.com>
from sqlalchemy import select, update, insert, delete

from src.ump.metadata.meta import DeployMeta
from src.ump.modules.deploy.model import UmpDeployInfo, UmpDeployInstanceInfo
from src.ump.utils.dbutils import DB
from src.ump.utils import get_unique_id
from src.ump.msg import SUCCESS

DEPLOY_SUCCESS = "deploy success"
DEPLOY_FAILURE = "deploy failure"
DEPLOY_CURRENT = "current"
DEPLOY_COMPLETED = "completed"


# 部署模块数据提供类
class DeployMeataInstance(DeployMeta):
    def get_deploy_success_hosts(self, deploy_name) -> []:
        d = self.get_deploy_success_hosts_info(deploy_name)
        h = []
        for i in d:
            h.append(i["deploy_host"])
        return h

    def get_deploy_success_hosts_info(self, deploy_name) -> []:
        db = DB()
        conn = db.get_connect()
        deploy_info = select(UmpDeployInstanceInfo, UmpDeployInfo).where(
            UmpDeployInfo.deploy_id == UmpDeployInstanceInfo.deploy_id,
            UmpDeployInfo.deploy_name == deploy_name,
            UmpDeployInfo.deploy_status == DEPLOY_CURRENT,
            UmpDeployInstanceInfo.deploy_status == DEPLOY_SUCCESS)
        hosts_rs = conn.execute(deploy_info)
        hosts_info = []
        for r in hosts_rs:
            row = {
                "id": r.id,
                "deploy_name": r.deploy_name,
                "deploy_group": r.deploy_group,
                "app_path": r.deploy_path,
                "deploy_host": r.deploy_host,
            }
            hosts_info.append(row)
        conn.close()
        return hosts_info


class DeployService:
    def __init__(self):
        db = DB()
        self.conn = db.get_connect()

    def get_current_deploy_id_and_app(self, deploy_name):
        rows = self.get_deploy_info(deploy_name)
        if rows is None:
            return None
        if len(rows) == 1:
            row = rows[0]
            deploy = {
                "deploy_id": row["deploy_id"],
                "deploy_app": row["deploy_app"]
            }
            return deploy

    def get_deploy_info(self, deploy_name=None, history=False):
        deploy_rows = []
        if history:
            s = select(UmpDeployInfo).where(UmpDeployInfo.deploy_name == deploy_name)
            rs = self.conn.execute(s)
            for r in rs:
                row = {
                    "deploy_id": r.deploy_id,
                    "deploy_name": r.deploy_name,
                    "deploy_path": r.deploy_path,
                    "deploy_app": r.deploy_app,
                    "deploy_app_last": r.deploy_app_last,
                    "deploy_group": r.deploy_group,
                    "host_num": r.deploy_host_num,
                    "failed_num": r.deploy_failure_num,
                    "deploy_status": r.deploy_status,
                    "deploy_date": r.deploy_time.strftime("%Y-%m-%d %H:%M:%S")
                }
                deploy_rows.append(row)
        else:
            s = select(UmpDeployInfo).where(UmpDeployInfo.deploy_status == DEPLOY_CURRENT,
                                            UmpDeployInfo.deploy_name == deploy_name)
            rs = self.conn.execute(s).fetchone()
            if rs is None:
                return None
            row = {
                "deploy_id": rs["deploy_id"],
                "deploy_name": rs["deploy_name"],
                "deploy_path": rs["deploy_path"],
                "deploy_app": rs["deploy_app"],
                "deploy_app_last": rs["deploy_app_last"],
                "deploy_group": rs["deploy_group"],
                "host_num": rs["deploy_host_num"],
                "failure_num": rs["deploy_failure_num"],
                "deploy_status": rs["deploy_status"],
                "deploy_date": rs["deploy_time"].strftime("%Y-%m-%d %H:%M:%S")
            }
            deploy_rows.append(row)
        return deploy_rows

    def create_new_deploy(self, prev_deploy_id=None,
                          prev_deploy_app=None,
                          deploy_name=None,
                          deploy_path=None,
                          deploy_app=None,
                          deploy_group=None,
                          deploy_comment=None,
                          success_hosts=None,
                          failure_hosts=None
                          ):
        if success_hosts is None:
            success_hosts = []
        with self.conn.begin():
            s1 = update(UmpDeployInfo). \
                where(UmpDeployInfo.deploy_name == deploy_name). \
                values({"deploy_status": DEPLOY_COMPLETED})
            self.conn.execute(s1)
            new_deploy_id = get_unique_id()
            new_deploy_info = {
                "deploy_id": new_deploy_id,
                "deploy_name": deploy_name,
                "deploy_path": deploy_path,
                "deploy_app": deploy_app,
                "deploy_group": deploy_group,
                "deploy_app_last": prev_deploy_app,
                "deploy_host_num": len(success_hosts) + len(failure_hosts),
                "deploy_failure_num": len(failure_hosts),
                "deploy_comment": deploy_comment,
            }
            # 更新部署状态
            s2 = insert(UmpDeployInfo).values(new_deploy_info)
            self.conn.execute(s2)
            instance_rows = []
            for h in success_hosts:
                v = {
                    "instance_id": get_unique_id(),
                    "deploy_id": new_deploy_id,
                    "instance_host": h,
                    "instance_status": DEPLOY_SUCCESS
                }
                instance_rows.append(v)
            for h in failure_hosts:
                v = {
                    "instance_id": get_unique_id(),
                    "deploy_id": new_deploy_id,
                    "instance_host": h,
                    "instance_status": DEPLOY_FAILURE
                }
                instance_rows.append(v)
            # 删除旧实例信息
            s3 = delete(UmpDeployInstanceInfo).where(UmpDeployInstanceInfo.deploy_id == prev_deploy_id)
            self.conn.execute(s3)
            # 更新新部署实例信息
            s4 = insert(UmpDeployInstanceInfo).values(instance_rows)
            self.conn.execute(s4)

    def delete_deploy(self, deploy_name):
        s = select(UmpDeployInfo). \
            where(UmpDeployInfo.deploy_status == DEPLOY_CURRENT,
                  UmpDeployInfo.deploy_name == deploy_name)
        rs = self.conn.execute(s).fetchone()
        if rs is None:
            return None
        deploy_id = rs["deploy_id"]
        s1 = delete(UmpDeployInfo).where(UmpDeployInfo.deploy_name == deploy_name)
        self.conn.execute(s1)
        s2 = delete(UmpDeployInstanceInfo).where(UmpDeployInstanceInfo.deploy_id == deploy_id)
        self.conn.execute(s2)
        return SUCCESS

    def get_deploy_instance_info(self, deploy_name):
        detail = select(UmpDeployInfo, UmpDeployInstanceInfo).\
            where(UmpDeployInfo.deploy_id == UmpDeployInstanceInfo.deploy_id,
                  UmpDeployInfo.deploy_name == deploy_name,
                  UmpDeployInfo.deploy_status == DEPLOY_CURRENT)
        rs = self.conn.execute(detail)
        instance_info_rows = []
        for r in rs:
            row = {
                "deploy_name": r.deploy_name,
                "instance_id": r.instance_id,
                "instance_host": r.instance_host,
                "instance_status": r.instance_status,
                "deploy_date": r.deploy_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            instance_info_rows.append(row)
        return instance_info_rows

    def close_db_connection(self):
        self.conn.close()
