# (c) 2021, xanthus tan <tanxk@neusoft.com>

# 模块返回状态值
SUCCESS = 200
FAILED = 500
WARN = 400

# UMP状态码
client_prompt = {
    200: "Command was completed successful!",
    # 警告信息
    401: "UMP Waring: The client could not match in current ump version. please update your client !",
    # 错误信息
    500: "UMP Error: not found such module",
    501: "UMP Error: missing key of action"
}

# 客户端接收到的信息体
message = {
    "code": 200,  # 默认值
    "msg": ""
}


