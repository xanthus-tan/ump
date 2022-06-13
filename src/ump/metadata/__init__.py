# (c) 2021, xanthus tan <tanxk@neusoft.com>
import abc
import os

import yaml

ump_home = os.path.abspath("")
config_path = os.path.join(ump_home, "conf")
hosts_file = os.path.join(config_path, "hosts")
datafile = os.path.join(config_path, "ump.db")
module_path = os.path.join(config_path, "modules")
CONFIG_FILE = "ump.yaml"


def ump_config_yaml():
    with open(os.path.join(config_path, CONFIG_FILE), encoding='utf-8') as f:
        y = yaml.safe_load(f)
        return y["ump"]


class Meta(abc.ABCMeta):
    @staticmethod
    def get_meta_info(self, name, tag):
        pass
