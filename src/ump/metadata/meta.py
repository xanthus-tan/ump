# (c) 2021, xanthus tan <tanxk@neusoft.com>
from abc import ABC, abstractmethod


class HostsMeta(ABC):

    @abstractmethod
    def get_host_info(self, group_id, host_ip):
        pass

    @abstractmethod
    def get_host_online_info(self, group_id):
        pass


class DeployMeta(ABC):

    @abstractmethod
    def get_deploy_success_hosts(self, deploy_name) -> []:
        return []

    @abstractmethod
    def get_deploy_success_hosts_info(self, deploy_name) -> []:
        return []
