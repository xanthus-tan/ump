# (c) 2021, xanthus tan <tanxk@neusoft.com>


# 客户端响应信息
class Response:
    def __init__(self):
        self.module_response = {
            "display": [],
            "module_status": 200,
            "parameter": {},
            "module_name": ""
        }

    def set_display(self, display: []):
        self.module_response["display"] = display

    def set_module_status_code(self, code: int):
        self.module_response["module_status"] = code

    def set_parameter(self, k, v):
        self.module_response["parameter"] = {k: v}

    def set_module_name(self, name):
        self.module_response["module_name"] = name

    def get_response(self):
        return self.module_response
