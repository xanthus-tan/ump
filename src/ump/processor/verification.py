# (c) 2021, xanthus tan <tanxk@neusoft.com>

import yaml

from src.ump.metadata.module import Module


# 指令过滤类
class InstructionFilter:
    def __init__(self):
        pass

    # 提取运行模块的指令
    def extract_instruction(self, json):
        attr = {}
        code = 200
        input_instruction = json
        input_arg_module = input_instruction["module"]
        input_arg_group = input_instruction["group"]
        input_arg_action = input_instruction["action"]
        input_arg_name = input_instruction["name"]
        input_arg_comment = input_instruction["comment"]
        module = Module()
        try:
            module_define = module.get_module_define(input_arg_module)
        except FileNotFoundError as fileNotFound:
            code = 500
            return code, attr
        except yaml.YAMLError as error:
            code = 501
            return code, attr
        module_define_instruction = self._extract_module_define_instruction(module_define)
        code, attr = self._filter_arg(input_instruction, module_define_instruction)
        attr["module"] = input_arg_module
        attr["group"] = input_arg_group
        attr["action"] = input_arg_action
        attr["name"] = input_arg_name
        attr["comment"] = input_arg_comment
        return code, attr

    # 获取模块定义的指令
    def _extract_module_define_instruction(self, module_define):
        args = module_define["module"]["args"]
        return args

    # 过滤相对应指令
    def _filter_arg(self, input_instruction, module_define_instruction):
        attr = {}
        instruction = {}
        status_code = 200
        for instruction_attribute in module_define_instruction:
            arg_value = ""
            name = instruction_attribute["name"]
            default_value = instruction_attribute["default"]
            try:
                arg_value = input_instruction[name]
            except KeyError as error:
                status_code = 401
            if arg_value == "":
                arg_value = default_value
            instruction[name] = arg_value
        attr["instruction"] = instruction
        return status_code, attr
