# (c) 2021, xanthus tan <tanxk@neusoft.com>

from abc import abstractmethod, ABC
from src.ump.utils.logger import logger
from src.ump.msg.module import Response

module_names = ["deploy", "release", "hosts", "instance", "monitor"]


# 模块抽象父类
class ActionBase(ABC):

    def __init__(self):
        self.insid = ""
        self.config = None
        self.action = ""
        self.group = ""
        self.module_name = ""
        self.name = ""
        self.comment = ""
        self.instruction = {}
        self.response = None

    def execute(self, arg, config) -> Response:
        # debug信息
        # 显示模块接收到的参数
        logger.debug(arg)
        self.instruction = arg["instruction"]
        self.action = arg["action"]
        self.module_name = arg["module"]
        self.group = arg["group"]
        self.name = arg["name"]
        self.comment = arg["comment"]
        self.config = config
        self.response = Response()
        self.response.set_module_name(self.module_name)
        # 显示默认值
        self.response.set_display([{"Info": "OK!"}])
        # 动态调用 set | get | delete
        status = eval("self." + self.action)(self.instruction)
        self.response.set_module_status_code(status)
        return self.response

    @abstractmethod
    def get(self, instruction):
        pass

    @abstractmethod
    def set(self, instruction):
        pass

    @abstractmethod
    def delete(self, instruction):
        pass
