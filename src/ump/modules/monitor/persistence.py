# (c) 2021, xanthus tan <tanxk@neusoft.com>
import json


class Metrics:
    def __init__(self):
        pass

    # 保存到日志
    def to_log(self, metrics_list):
        with open("D:/workspaces/pycharm/ump/logs/metrics.log", "a") as file:
            # write to file
            for m in metrics_list:
                s = json.dumps(m)
                file.writelines(s + "\n")

    # 保存到es
    def to_es(self):
        pass
