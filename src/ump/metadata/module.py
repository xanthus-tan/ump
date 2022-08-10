# (c) 2021, xanthus tan <tanxk@neusoft.com>

import os
import yaml
from src.ump.modules.hosts.meta import HostsMetaInstance
from src.ump.modules.deploy.meta import DeployMetaInstance, DeployInstanceMetaInstance
from src.ump.modules.release.meta import ReleaseMetaInstance
from src.ump.metadata import module_path
from src.ump.utils import LINUX_SEP


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
        self.deploy_meta = DeployMetaInstance()
        self.instance_meta = DeployInstanceMetaInstance()

    def get_deploy_success_hosts(self, deploy_name) -> []:
        return self.deploy_meta.get_deploy_success_hosts(deploy_name)

    def get_deploy_group(self, deploy_name):
        return self.deploy_meta.get_deploy_group(deploy_name)

    def get_deploy_success_hosts_info(self, deploy_name) -> []:
        return self.deploy_meta.get_deploy_success_hosts_info(deploy_name)

    def get_deploy_path(self, deploy_name):
        return self.deploy_meta.get_deploy_path(deploy_name)

    def get_instance_group_and_host(self, instance_id):
        return self.deploy_meta.get_instance_group_and_host(instance_id)

    def get_instance_pid(self, instance_id):
        return self.instance_meta.get_deploy_instance_pid(instance_id)

    def get_started_instance_info(self, deploy_name):
        return self.instance_meta.get_deploy_started_instance(deploy_name)

    def get_current_deploy_info(self, deploy_name):
        return self.deploy_meta.get_deploy_info(deploy_name)

    def get_app_info(self, instance_id):
        return self.instance_meta.get_deploy_instance_info(instance_id)

    def get_app_path(self, instance_id):
        instance_info = self.get_app_info(instance_id)
        app_path = instance_info["app_path"]
        return app_path

    def get_app_log_path(self, instance_id):
        app_path = self.get_app_path(instance_id)
        basedir = os.path.dirname(app_path)
        log_name = "app.log"
        log_path = basedir + LINUX_SEP + log_name
        return log_path

