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
    def get_instance_group_and_host(self, instance_id):
        pass

    @abstractmethod
    def get_deploy_group(self, deploy_name):
        pass

    @abstractmethod
    def get_deploy_success_hosts(self, deploy_name) -> []:
        return []

    @abstractmethod
    def get_deploy_success_hosts_info(self, deploy_name) -> []:
        return []

    @abstractmethod
    def get_deploy_path(self, deploy_name):
        pass

    @abstractmethod
    def get_deploy_id(self, deploy_name):
        pass


class DeployInstanceMeta(ABC):
    @abstractmethod
    def get_deploy_instance_pid(self, instance_id):
        pass

    @abstractmethod
    def get_deploy_started_instance(self, deploy_name):
        pass
