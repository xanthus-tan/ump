# (c) 2021, xanthus tan <tanxk@neusoft.com>
from abc import ABC

import sqlalchemy
from sqlalchemy import insert, delete
from sqlalchemy.sql import select
from src.ump.msg import FAILED
from src.ump.modules.hosts.model import UmpHostsInfo, HOST_ONLINE
from src.ump.metadata.meta import HostsMeta
from src.ump.utils.dbutils import DB
from src.ump.utils.logger import logger


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


class HostService:
    def __init__(self):
        db = DB()
        self.conn = db.get_connect()

    def get_host_info(self, group_id):
        rows = []
        if group_id == "":
            s = select(UmpHostsInfo).where(UmpHostsInfo.status == HOST_ONLINE)
        else:
            s = select(UmpHostsInfo).where(UmpHostsInfo.group_id == group_id, UmpHostsInfo.status == HOST_ONLINE)
        rs = self.conn.execute(s)
        for r in rs:
            row = {"address": r.address,
                   "group": r.group_id,
                   "date": r.register_time.strftime("%Y-%m-%d"),
                   "user": r.login_username,
                   "password": r.login_password
                   }
            rows.append(row)
        return rows

    def register_host(self, hosts=None, default_port=None, group_name=None, user=None, password=None):
        insert_values = []
        for url in hosts:
            url = url.split(":")
            ip = url[0]
            port = default_port
            if len(url) > 1:
                port = url[1]
            v = {"address": ip, "port": port, "group_id": group_name,
                 "login_username": user, "login_password": password}
            insert_values.append(v)
        s = insert(UmpHostsInfo).values(insert_values)
        try:
            r = self.conn.execute(s)
            update_count = r.rowcount
        except sqlalchemy.exc.IntegrityError as error:
            logger.error(error)
            return FAILED
        return update_count

    def delete_host_by_group(self, group_name):
        s = delete(UmpHostsInfo).where(UmpHostsInfo.group_id == group_name)
        r = self.conn.execute(s)
        return r.rowcount

    def delete_host_by_address(self, address):
        s = delete(UmpHostsInfo).where(UmpHostsInfo.address == address)
        r = self.conn.execute(s)
        return r.rowcount

    def close_db_connection(self):
        self.conn.close()
