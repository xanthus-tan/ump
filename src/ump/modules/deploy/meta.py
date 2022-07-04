# (c) 2021, xanthus tan <tanxk@neusoft.com>
from sqlalchemy import select, update, insert, delete

from src.ump.metadata.meta import DeployMeta
from src.ump.modules.deploy.model import UmpDeployInfo, UmpDeployInstanceInfo
from src.ump.utils.dbutils import DB
from src.ump.utils import get_unique_id

SUCCESS = "deploy success"
FAILURE = "deploy failure"
CURRENT = "current"
COMPLETED = "completed"


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
            UmpDeployInfo.deploy_status == CURRENT,
            UmpDeployInstanceInfo.deploy_status == SUCCESS)
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

    def get_current_deploy_info(self, deploy_name):
        s = select(UmpDeployInfo). \
            where(UmpDeployInfo.deploy_status == CURRENT,
                  UmpDeployInfo.deploy_name == deploy_name)
        rs = self.conn.execute(s).fetchone()
        if rs is not None:
            deploy = {
                "deploy_id": rs["deploy_id"],
                "deploy_app": rs["deploy_app"]
            }
            return deploy
        else:
            return None

    def create_new_deploy(self, prev_deploy_id=None,
                          prev_deploy_app=None,
                          deploy_name=None,
                          deploy_path=None,
                          deploy_app=None,
                          deploy_group=None,
                          deploy_comment=None,
                          success_hosts=[],
                          failure_hosts=[]
                          ):
        with self.conn.begin:
            s1 = update(UmpDeployInfo). \
                where(UmpDeployInfo.id == prev_deploy_id). \
                values({"deploy_status": COMPLETED})
            self.conn.execute(s1)
            new_deploy_id = get_unique_id()
            new_deploy_info = {
                "deploy_id": new_deploy_id,
                "deploy_name": deploy_name,
                "deploy_path": deploy_path,
                "deploy_app": deploy_app,
                "deploy_group": deploy_group,
                "deploy_app_last": prev_deploy_app,
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
                    "instance_status": SUCCESS
                }
                instance_rows.append(v)
            for h in failure_hosts:
                v = {
                    "instance_id": get_unique_id(),
                    "deploy_id": new_deploy_id,
                    "instance_host": h,
                    "instance_status": FAILURE
                }
                instance_rows.append(v)
            # 删除旧实例信息
            s3 = delete(UmpDeployInstanceInfo).where(UmpDeployInstanceInfo.deploy_id == prev_deploy_id)
            self.conn.execute(s3)
            # 更新新部署实例信息
            s4 = insert(UmpDeployInstanceInfo).value(instance_rows)
            self.conn.execute(s4)

    def close_db_connection(self):
        self.conn.close()

