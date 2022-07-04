# (c) 2021, xanthus tan <tanxk@neusoft.com>
from abc import ABC

from sqlalchemy.sql import select
from src.ump.modules.hosts.model import UmpHostsInfo, HOST_ONLINE
from src.ump.metadata.meta import HostsMeta
from src.ump.utils.dbutils import DB


class HostsMetaInstance(HostsMeta, ABC):
    def get_host_online_info(self, group_id):
        db = DB()
        conn = db.get_connect()
        s = select(UmpHostsInfo).where(UmpHostsInfo.status == HOST_ONLINE, UmpHostsInfo.group_id == group_id)
        rs = conn.execute(s)
        hosts = []
        for r in rs:
            row = {
                "addr": r.address,
                "port": r.port,
                "username": r.login_username,
                "password": r.login_password
            }
            hosts.append(row)
        conn.close()
        return hosts

    def get_host_info(self, group_id, host_ip) -> {}:
        db = DB()
        conn = db.get_connect()
        s = select(UmpHostsInfo) \
            .where(UmpHostsInfo.group_id == group_id,
                   UmpHostsInfo.address == host_ip)
        rs = conn.execute(s).fetchone()
        # key值名称不能修改,获取ssh连接时,会根据key获取相关信息
        host = {
            "addr": rs.address,
            "port": rs.port,
            "username": rs.login_username,
            "password": rs.login_password
        }
        conn.close()
        return host
