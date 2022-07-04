# (c) 2021, xanthus tan <tanxk@neusoft.com>

import os
import yaml

from src.ump.modules.hosts.meta import HostsMetaInstance
from src.ump.modules.deploy.meta import DeployMeataInstance
from src.ump.modules.release.meta import ReleaseMetaInstance
from src.ump.metadata import module_path


class Module:
    def __init__(self):
        self.module_defile_file_suffix = ".yaml"

    def get_module_define(self, name):
        module_define_file = name + self.module_defile_file_suffix
        with open(os.path.join(module_path, module_define_file), encoding='utf-8') as yaml_file:
            module_define = yaml.safe_load(yaml_file)
            return module_define


class HostsModule:
    def __init__(self):
        self.meta = HostsMetaInstance()

    def get_host_username(self, group_id, host_ip):
        pass

    def get_host_password(self, group_id, host_ip):
        pass

    def get_host_info(self, group_id, host_ip):
        return self.meta.get_host_info(group_id, host_ip)


class ReleaseModule:
    def __init__(self, name, tag):
        meta = ReleaseMetaInstance()
        self.info = meta.get_meta_info(name, tag)

    def get_file_id(self):
        return self.info["file_id"]

    def get_file_suffix(self):
        return self.info["app_suffix"]


class DeployModule:
    def __init__(self):
        self.meta = DeployMeataInstance()

    def get_deploy_success_hosts(self, deploy_name) -> []:
        return self.meta.get_deploy_success_hosts(deploy_name)

    def get_deploy_success_hosts_info(self, deploy_name) -> []:
        return self.meta.get_deploy_success_hosts_info(deploy_name)
