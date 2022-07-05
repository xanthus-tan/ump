# (c) 2021, xanthus tan <tanxk@neusoft.com>
import re

import sqlalchemy
from sqlalchemy.sql import select, delete, insert

from src.ump.modules.hosts.meta import HostService
from src.ump.utils.logger import logger
from src.ump.modules import ActionBase
from src.ump.modules.hosts.model import UmpHostsInfo, HOST_ONLINE
from src.ump.msg import SUCCESS, WARN, FAILED
from src.ump.utils.dbutils import DB


# hosts模块具体实现
class Action(ActionBase):

    def __init__(self):
        super().__init__()
        self.conn = DB()

    def get(self, instruction):
        group_name = self.group
        host_service = HostService()
        rows = host_service.get_host_info(group_name)
        host_service.close_db_connection()
        self.response.set_display(rows)
        return SUCCESS

    def set(self, instruction):
        password = instruction["password"]
        user = instruction["user"]
        group_name = self.group
        address_list = instruction["address"].split(",")
        host_service = HostService()
        default_port = self.config.get_ssh_default_port()
        info = host_service.register_host(hosts=address_list,
                                          default_port=default_port,
                                          group_name=group_name,
                                          user=user,
                                          password=password)
        host_service.close_db_connection()
        if info == FAILED:
            self.response.set_display([{"Error": "host duplicated"}])
            return FAILED
        display = [{"Info": str(info) + " rows updated"}]
        self.response.set_display(display)
        return SUCCESS

    def delete(self, instruction):
        group_name = self.group
        addr = instruction["address"]
        host_service = HostService()
        ip_reg = "(([01]{0,1}\\d{0,1}\\d|2[0-4]\\d|25[0-5])\\.){3}([01]{0,1}\\d{0,1}\\d|2[0-4]\\d|25[0-5])"
        if group_name == "" or group_name is None:
            self.response.set_display([{"Warn": "group value is missing!"}])
            return WARN
        if addr is None:
            info = host_service.delete_host_by_group(group_name=group_name)
        elif re.match(ip_reg, addr):
            info = host_service.delete_host_by_address(group_name, addr)
        else:
            self.response.set_display([{"Info": "not found host or group"}])
            return WARN
        self.response.set_display([{"Info": "delete rows " + str(info)}])
        return SUCCESS
