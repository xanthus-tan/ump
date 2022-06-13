# (c) 2021, xanthus tan <tanxk@neusoft.com>
import re

from sqlalchemy.sql import select, delete, insert

from src.ump.modules import ActionBase
from src.ump.modules.hosts.model import UmpHostsInfo, HOST_ONLINE
from src.ump.msg import SUCCESS
from src.ump.utils.dbutils import DB


# hosts模块具体实现
class Action(ActionBase):

    def __init__(self):
        super().__init__()
        self.conn = DB()

    def get(self, instruction):
        rows = []
        group_name = self.group
        conn = self.conn.get_connect()
        if group_name == "":
            s = select(UmpHostsInfo).where(UmpHostsInfo.status == HOST_ONLINE)
        else:
            s = select(UmpHostsInfo).where(UmpHostsInfo.group_id == group_name, UmpHostsInfo.status == HOST_ONLINE)
        rs = conn.execute(s)
        for r in rs:
            row = {"address": r.address,
                   "group": r.group_id,
                   "date": r.register_time.strftime("%Y-%m-%d"),
                   "user": r.login_username,
                   "password": r.login_password
                   }
            rows.append(row)
        conn.close()
        self.response.set_display(rows)
        return SUCCESS

    def set(self, instruction):
        password = instruction["password"]
        user = instruction["user"]
        group_name = self.group
        address_list = instruction["address"].split(",")
        insert_values = []
        for adr in address_list:
            v = {"address": adr, "group_id": group_name, "login_username": user, "login_password": password}
            insert_values.append(v)
        conn = self.conn.get_connect()
        s = insert(UmpHostsInfo).values(insert_values)
        r = conn.execute(s)
        conn.close()
        display = [{"Info": str(r.rowcount) + " rows updated"}]
        self.response.set_display(display)
        return SUCCESS

    def delete(self, instruction):
        group_name = self.group
        conn = self.conn.get_connect()
        addr = instruction["address"]
        ip_reg = "(([01]{0,1}\\d{0,1}\\d|2[0-4]\\d|25[0-5])\\.){3}([01]{0,1}\\d{0,1}\\d|2[0-4]\\d|25[0-5])"
        is_ip = re.match(ip_reg, addr)
        if is_ip:
            s = delete(UmpHostsInfo).where(UmpHostsInfo.address == addr)
        else:
            s = delete(UmpHostsInfo).where(UmpHostsInfo.group_id == group_name)
        r = conn.execute(s)
        conn.close()
        display = [{"Info": "delete rows " + str(r.rowcount)}]
        self.response.set_display(display)
        return SUCCESS
