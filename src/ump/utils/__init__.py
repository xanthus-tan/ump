# (c) 2021, xanthus tan <tanxk@neusoft.com>

import time
import uuid
from datetime import datetime


# 获取当前时间datetime类型, 数据库插入时会用到
def get_current_local_datetime():
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")


# 获取当前时间str类型
def current_time_str():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# 获取当前日期str类型
def current_date_str():
    return time.strftime("%Y%m%d", time.localtime())


# 获取UUID
def get_unique_id():
    uuid_value = uuid.uuid1()
    return str(uuid_value).replace("-", "")


# 获取当前时间戳
def get_current_timestamp():
    # t = int(round(t * 1000))  # 毫秒级时间戳
    t = int(time.time())
    return str(t)

