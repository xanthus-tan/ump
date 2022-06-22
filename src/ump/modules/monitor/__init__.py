# (c) 2021, xanthus tan <tanxk@neusoft.com>
import copy
import json
import os

from src.ump.exector.remote import Connector, RemoteHandler
from src.ump.exector.scheduler import Job
from src.ump.modules import ActionBase
from src.ump.modules.monitor.persistence import MetricsToES, MetricsToFile, MetricsDestinationInfo
from src.ump.msg import SUCCESS, FAILED, WARN
from src.ump.utils import get_unique_id, current_time_str
from src.ump.utils.logger import logger

# 监控状态
monitor_status = {
    "id": None,
    "group": None,
    "freq": None,
    "status": "",
    "start_time": ""
}

status_list = []

# 监控模块具体实现
class Action(ActionBase):
    def get(self, instruction):
        if instruction["type"] == "status":
            display = status_list
            self.response.set_display(display)
            return SUCCESS
        if instruction["type"] == "metrics":
            if self.group is None or self.group == '':
                display = [{"Error": "missing parameter of group"}]
                self.response.set_display(display)
                return FAILED
            c = Connector()
            ssh_pool = c.get_ssh_pool(self.group)
            handler = RemoteHandler(self.config.get_ssh_timeout())
            cpath = instruction["cpath"]
            metrics = []
            failed_hosts = []
            if cpath != "":
                metrics, failed_hosts = handler.remote_shell(ssh_pool, cpath)
            if len(metrics) == 0:
                display = [{"Waring": "Noting"}]
                self.response.set_display(display)
                return WARN
            v = display_metrics(metrics, failed_hosts)
            c.close_ssh_connect()
            display = v
            self.response.set_display(display)
            return SUCCESS
        display = [{"Error": "missing parameter of type"}]
        self.response.set_display(display)
        return FAILED

    def set(self, instruction):
        if instruction["collector"]:
            locale_collector = self.config.get_collector_path()
            cpath = instruction["cpath"]
            c1 = Connector()
            ssh_pool = c1.get_ssh_pool(self.group)
            handler = RemoteHandler(self.config.get_ssh_timeout())
            dir_name = os.path.dirname(cpath)
            sh, fh = handler.remote_shell(ssh_pool, "mkdir -p " + dir_name)
            c1.close_ssh_connect()
            c2 = Connector()
            ssh_pool = c2.get_ssh_pool(self.group)
            # 简单写法，数据量少性能不会有太大影响
            for s in ssh_pool:
                for h in fh:
                    if s.get_address() == h:
                        ssh_pool.remove(s)
            handler.remote_copy(ssh_pool, locale_collector, cpath)
            handler.remote_shell(ssh_pool, "chmod +x " + cpath)
            self.response.set_display([{"The collector tool deploy to node":
                                        "success: " + str(len(sh)) +
                                        "\n" +
                                        "failed: " + str(len(fh))}])
            c2.close_ssh_connect()
            return SUCCESS
        if instruction["auto"]:
            file_status = self.config.get_metrics_to_file_enable_status()
            es_status = self.config.get_metrics_to_es_enable_status()
            obj = None
            if file_status.lower() == "true":
                des = MetricsDestinationInfo(log_path=self.config.get_metrics_to_file_path())
                obj = MetricsToFile(des)
            elif es_status.lower() == "true":
                des = MetricsDestinationInfo(es_username=self.config.get_metrics_to_es_username(),
                                             es_pwd=self.config.get_metrics_to_es_password(),
                                             es_url=self.config.get_metrics_to_es_url(),
                                             es_cert=self.config.get_metrics_to_es_cert_path())
                obj = MetricsToES(des)
            else:
                display = [{"Error": "metrics not destination, file or es?"}]
                self.response.set_display(display)
                return FAILED
            c3 = Connector()
            ssh_pool = c3.get_ssh_pool(self.group)
            job = Job()
            job_id = get_unique_id()
            interval = instruction["freq"]
            job.set_job_interval(int(interval))
            job.set_job_id(job_id)
            job.set_job_func(metrics_to_log, args=[obj, ssh_pool, instruction["cpath"], self.config.get_ssh_timeout()])
            job.job_start()
            m = copy.deepcopy(monitor_status)
            m["id"] = job_id
            m["group"] = self.group
            m["freq"] = interval + "s"
            m["status"] = "run"
            m["start_time"] = current_time_str()
            status_list.append(m)
            display = [m]
            self.response.set_display(display)
            c3.close_ssh_connect()
        return SUCCESS

    def delete(self, instruction):
        job = Job()
        job_id = instruction["jobid"]
        if job_id:
            job.job_stop(job_id)
            remove_monitor(job_id)
            display = [{"Info": "job has been deleted, id is " + job_id}]
            self.response.set_display(display)
            return SUCCESS
        if self.group:
            job_id = get_job_id(self.group)
            if job_id is None:
                display = [{"Warning": "not found the job"}]
                self.response.set_display(display)
                return WARN
            job.job_stop(job_id)
            remove_monitor(job_id)
            display = [{"Info": "job has been deleted" + job_id}]
            self.response.set_display(display)
            return SUCCESS
        display = [{"Warning": "not found the job"}]
        self.response.set_display(display)
        return WARN


def metrics_to_log(destination, ssh, collector_path, timeout):
    handler = RemoteHandler(timeout)
    metrics_list, f = handler.remote_shell(ssh, collector_path)
    destination.write(metrics_list)


# 通过组名称获取job id
def get_job_id(group):
    for monitor in status_list:
        if monitor["group"] == group:
            return monitor["id"]
    return None


# 移除监控结果
def remove_monitor(job_id):
    for monitor in status_list:
        if monitor["id"] == job_id:
            status_list.remove(monitor)


# 格式化输出监控指标
"""
[{'cpu': {'CpuPercent': 12.060301507506397, 'CpuCount': 2}, 
'mem': {'total': 4082409472, 'available': 2342199296, 'used': 1485053952, 'free': 1456881664}, 
'disk': [{'device': '/dev/sda5', 'total': 31040933888, 'free': 17140072448, 'used': 12300472320, 'fstype': 'ext4', 'mountpoint': '/'}, 
{'device': '/dev/sda1', 'total': 535805952, 'free': 535801856, 'used': 4096, 'fstype': 'vfat', 'mountpoint': '/boot/efi'}], 
'time': '2022-03-07 17:50:16',
 'host': '192.168.72.130'}
"""


def display_metrics(metrics, failed_hosts):
    # debug 信息
    logger.debug(metrics)
    display = []
    host_metrics = {}
    for m in metrics:
        try:
            out = m["out"]
            print(out)
            host_metrics = json.loads(out)
            print(host_metrics)
        except json.decoder.JSONDecodeError as error:
            logger.error("to json info error, from monitor module")
            logger.error("json error" + str(error))
        row = {"host": m["host"]}
        cpu = host_metrics["cpu"]
        cpu_display = "core:" + str(cpu["CpuCount"]) + " " + \
                      "used:" + str(round(cpu["CpuPercent"], 2)) + "%"
        row["cpu"] = cpu_display
        mem = host_metrics["mem"]
        mem_display = "total:" + str(round(mem["total"] / 1024 / 1024 / 1024, 2)) + " " + \
                      "used:" + str(round(mem["used"] / 1024 / 1024 / 1024, 2))
        row["memory (unit: GB)"] = mem_display
        disk = host_metrics["disk"]
        disk_info = ""
        for d in disk:
            disk_info += "point:" + d["mountpoint"] + \
                         " type:" + d["fstype"] + \
                         " total:" + str(round(d["total"] / 1024 / 1024 / 1024, 2)) + \
                         " used:" + str(round(d["used"] / 1024 / 1024 / 1024, 2)) + \
                         ", "
            # row["mountpoint " + d["mountpoint"] + " (unit: GB)"] = "type:" + d["fstype"] + " " + \
            #                                                        "total:" + str(
            #     round(d["total"] / 1024 / 1024 / 1024, 2)) + " " + \
            #                                                        "used:" + str(
            #     round(d["used"] / 1024 / 1024 / 1024, 2))
        row["disk (unit: GB)"] = disk_info[:-2]
        display.append(row)
    for h in failed_hosts:
        row = {"host": h, "cpu": "down", "memory": "down", "disk": "down"}
        display.append(row)
    return display
