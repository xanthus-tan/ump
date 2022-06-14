# (c) 2021, xanthus tan <tanxk@neusoft.com>
import json
import os
from abc import ABC, abstractmethod

import elastic_transport
from elasticsearch import Elasticsearch
from src.ump.metadata import ump_home
from src.ump.utils.logger import logger
from src.ump.utils import current_date_str


class MetricsDestinationInfo:
    def __init__(self, es_username="", es_pwd="", es_url="", es_cert="", log_path=""):
        self.es_username = es_username
        self.es_pwd = es_pwd
        self.es_url = es_url
        self.es_cert = es_cert
        self.log_path = log_path

    def get_es_username(self):
        return self.es_username

    def get_es_pwd(self):
        return self.es_pwd

    def get_es_url(self):
        return self.es_url

    def get_es_cert(self):
        return self.es_cert

    def get_log_path(self):
        return self.log_path


class Metrics(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def write(self, node_metrics_item):
        pass


# 指标保存到文件
class MetricsToFile(Metrics):
    def __init__(self, des_info):
        super().__init__()
        self.des_info = des_info

    def write(self, node_metrics_item):
        metrics_log_path = os.path.join(ump_home, self.des_info.get_log_path())
        with open(metrics_log_path, "a") as file:
            # write to file
            for m in node_metrics_item:
                s = json.dumps(m)
                file.writelines(s + "\n")


# 指标保存到ES
class MetricsToES(Metrics):
    def __init__(self, des_info):
        super().__init__()
        self.des_info = des_info

    def write(self, node_metrics_item):
        es_username = self.des_info.get_es_username()
        es_password = self.des_info.get_es_pwd()
        es_url = self.des_info.get_es_url()
        es_cert = self.des_info.get_es_cert()
        es = Elasticsearch(hosts=es_url,
                           ca_certs=os.path.join(ump_home, es_cert),
                           basic_auth=(es_username, es_password),
                           timeout=0.5
                           )
        current_date = current_date_str()
        cpu_index_name = "cpu-index-" + current_date
        mem_index_name = "mem-index-" + current_date
        disk_index_name = "disk-index-" + current_date
        for m in node_metrics_item:
            host_metrics = json.loads(m["out"])
            cpu = host_metrics["cpu"]
            mem = host_metrics["mem"]
            disks = host_metrics["disk"]
            cpu_doc = {
                "cpuPercent": cpu["CpuPercent"],
                "cpuNum": cpu["CpuCount"],
                "date": m["time"],
                "host": m["host"]
            }
            mem_doc = {
                "memTotal": mem["total"],
                "memAvailable": mem["available"],
                "memUsed": mem["used"],
                "memFree": mem["free"],
                "date": m["time"],
                "host": m["host"]
            }
            try:
                es.index(index=cpu_index_name, document=cpu_doc)
                es.index(index=mem_index_name, document=mem_doc)
            except elastic_transport.ConnectionTimeout as err:
                logger.error("elasticsearch error info: " + str(err))
                return
            es.indices.refresh(index="cpu-index")
            es.indices.refresh(index="mem-index")
            disk_doc = {}
            disk_device_count = 1
            for d in disks:
                disk_doc["device[" + str(disk_device_count) + "] name"] = d["device"]
                disk_doc["device[" + str(disk_device_count) + "] free"] = d["free"]
                disk_doc["device[" + str(disk_device_count) + "] used"] = d["used"]
                disk_doc["device[" + str(disk_device_count) + "] fstype"] = d["fstype"]
                disk_doc["device[" + str(disk_device_count) + "] mountpoint"] = d["mountpoint"]
                disk_device_count += 1
            disk_doc["date"] = m["time"]
            disk_doc["host"] = m["host"]
            try:
                es.index(index=disk_index_name, document=disk_doc)
            except elastic_transport.ConnectionTimeout as err:
                logger.error("elasticsearch error info: " + str(err))
                return
            es.indices.refresh(index="disk-index")
        logger.info("metrics to elasticsearch")
        es.close()
