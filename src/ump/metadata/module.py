# (c) 2021, xanthus tan <tanxk@neusoft.com>

import os

import yaml

from src.ump.metadata import module_path


class Module:
    def __init__(self):
        self.module_defile_file_suffix = ".yaml"

    def get_module_define(self, name):
        module_define_file = name + self.module_defile_file_suffix
        with open(os.path.join(module_path, module_define_file), encoding='utf-8') as yaml_file:
            module_define = yaml.safe_load(yaml_file)
            return module_define
