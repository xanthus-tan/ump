# (c) 2021, xanthus tan <tanxk@neusoft.com>

from sqlalchemy.exc import OperationalError

from src.ump.msg import message, client_prompt
from src.ump.processor.verification import InstructionFilter
from src.ump.utils.logger import logger


# 指令操作类
class InstructionHandler:
    def __init__(self, config):
        self.config = config

    def run(self, cmd, translate):
        json = translate.to_json(cmd)
        logger.debug("request json is {}".format(json))
        msg = self._parser(json)
        logger.debug("response json is {}".format(msg))
        return msg

    # 解析并且执行指令
    def _parser(self, json):
        fil = InstructionFilter()
        status_code, attr = fil.extract_instruction(json)
        message["code"] = status_code
        message["msg"] = client_prompt[status_code]
        if status_code >= 500:
            message["module"] = {"display": [{"Info": "Error"}]}
            return message
        module_name = attr["module"]
        module_class = "Action"
        try:
            my_handler = getattr(
                __import__("src.ump.modules.{0}".format(module_name), fromlist=[module_class]), module_class)
            print(my_handler)
            module = my_handler()
            res = module.execute(attr, self.config)
            message["module"] = res.get_response()
        except OperationalError as error:
            logger.error(error)
            message["code"] = 500
        except ModuleNotFoundError as error:
            logger.error("module error")
            logger.error(error)
            message["module"] = {"display": [{"Error": str(error)}]}
            message["code"] = 500
            message["msg"] = client_prompt[500]
            return message
        except SyntaxError as error:
            logger.error(error)
            logger.error("missing key word of action")
            message["code"] = 502
            message["msg"] = client_prompt[502]
        return message
