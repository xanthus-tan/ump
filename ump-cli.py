# (c) 2021, xanthus tan <tanxk@neusoft.com>
###############################################################
"""
cli example
hosts模块
  ump-cli.py --module hosts --action get --group g1
  ump-cli.py --module hosts --action set --group g1 --address 192.168.72.130,192.168.72.132 --user xanthus --password 1
monitor模块
  ump-cli.py --module monitor --action get --group g1 --type status
  ump-cli.py --module monitor --action get --group g1 --type metrics
  ump-cli.py --module monitor --action get --group g1 --cpath /home/xanthus/collector --type metrics
  ump-cli.py --module monitor --action set --group g1 --collector true
  ump-cli.py --module monitor --action set --group g1 --collector true --cpath /home/xanthus/ump/collector
  ump-cli.py --module monitor --action set --group g1 --auto true --freq 5
  ump-cli.py --module monitor --action set --group g1 --auto true --freq 5 --cpath /home/xanthus/ump/collector
  ump-cli.py --module monitor --action delete --jobid 5060cdf69b5f11ecb154a6fc7733a40b
release模块
  ump-cli.py --module release --action set --name demo-app --tag 1.0 --src d:\demo-app.jar
  # 查询全部部署
  ump-cli.py --module release --action get
  ump-cli.py --module release --action get --name demo-app
  ump-cli.py --module release --action delete --name demo-app --tag 1.0
deploy模块
  ump-cli.py --module deploy --action set --group g1 --name demo-deploy --app demo-app:1.0 --dest /tmp/
  ump-cli.py --module deploy --action get --name demo-deploy
  ump-cli.py --module deploy --action get --name demo-deploy --detail true
  ump-cli.py --module deploy --action get --name demo-deploy --history true
  ump-cli.py --module deploy --action delete --name demo-deploy
  ump-cli.py --module deploy --action delete --name demo-deploy --history true
service模块
  ump-cli.py --module instance --action get --deploy-name demo-deploy
  ump-cli.py --module instance --action set --deploy-name demo-deploy --control start
  ump-cli.py --module instance --action set --deploy-name demo-deploy --control stop
"""
import json
import optparse
import os
import socket
import requests
from prettytable import PrettyTable

# *******************版本*******************
UMP_CLI_VERSION = "1.1"
# *****************************************
HOST = socket.gethostname()
BUFFER_SIZE = 1024 * 8
REGISTRY_URL = "http://127.0.0.1:3002/registry/push"


def command_format():
    usage = "usage: ump-cli --module name --action [set|get|delete] [--hosts host's address] -arg1, -arg2"
    parser = optparse.OptionParser(usage, version="ump-client 1.0")
    parser.add_option("", "--module",
                      dest="module",
                      type="string",
                      help="module's name")
    parser.add_option("", "--group",
                      dest="group",
                      type="string",
                      help="group's name")
    parser.add_option("", "--action",
                      dest="action",
                      type="string",
                      help="set | get | delete")
    parser.add_option("", "--name",
                      dest="name",
                      type="string",
                      help="target name")
    parser.add_option("", "--comment",
                      dest="comment",
                      type="string",
                      help="operate comment")
    # monitor monitor moudle
    monitor_group = optparse.OptionGroup(parser, "monitor module")
    monitor_group.add_option("", "--freq",
                             dest="freq",
                             type="string",
                             help="monitor frequency")
    monitor_group.add_option("", "--type",
                             dest="type",
                             type="string",
                             help="device type")
    monitor_group.add_option("", "--cpath",
                             dest="cpath",
                             type="string",
                             help="collector tool path in node")
    monitor_group.add_option("", "--auto",
                             dest="auto",
                             type="string",
                             help="auto collector switch")
    monitor_group.add_option("", "--collector",
                             dest="collector",
                             type="string",
                             help="deploy collector")
    monitor_group.add_option("", "--jobid",
                             dest="jobid",
                             type="string",
                             help="job id")

    parser.add_option_group(monitor_group)

    # ump hosts moudle
    hosts_group = optparse.OptionGroup(parser, "hosts module")
    hosts_group.add_option("", "--address",
                           dest="address",
                           type="string",
                           help="hosts address")
    hosts_group.add_option("", "--password",
                           dest="password",
                           type="string",
                           help="hosts password")
    hosts_group.add_option("", "--user",
                           dest="user",
                           type="string",
                           help="hosts user")
    parser.add_option_group(hosts_group)

    # ump deploy moudle
    deploy_group = optparse.OptionGroup(parser, "deploy module")
    deploy_group.add_option("", "--dest",
                            dest="dest",
                            type="string",
                            help="deploy of target")
    deploy_group.add_option("", "--app",
                            dest="app",
                            type="string",
                            help="")
    deploy_group.add_option("", "--history",
                            dest="history",
                            type="string",
                            help="")
    deploy_group.add_option("", "--detail",
                            dest="detail",
                            type="string",
                            help="")
    deploy_group.add_option("", "--health",
                            dest="health",
                            type="string",
                            help="")
    parser.add_option_group(deploy_group)

    # ump release moudle
    release_group = optparse.OptionGroup(parser, "release module")
    release_group.add_option("", "--tag",
                             dest="tag",
                             type="string",
                             help="push file's tag")
    release_group.add_option("", "--src",
                             dest="src",
                             type="string",
                             help="file src")
    release_group.add_option("", "--size",
                             dest="size",
                             type="string",
                             help="")
    release_group.add_option("", "--originName",
                             dest="originName",
                             type="string",
                             help="")
    release_group.add_option("", "--originSuffix",
                             dest="originSuffix",
                             type="string",
                             help="")
    release_group.add_option("", "--filename",
                             dest="filename",
                             type="string",
                             help="")
    parser.add_option_group(release_group)

    # ump deploy moudle
    service_group = optparse.OptionGroup(parser, "instance module")
    service_group.add_option("", "--deploy-name",
                             dest="deploy-name",
                             type="string",
                             help="deploy name")
    service_group.add_option("", "--control",
                             dest="control",
                             type="string",
                             help="app start command")
    parser.add_option_group(service_group)
    return parser


def client():
    # parser server
    parser = command_format()
    (options, args) = parser.parse_args()
    if options.module is None:
        print(parser.usage)
        exit(0)
    port = 3003  # socket server port number
    client_socket = socket.socket()  # instantiate
    client_socket.connect((HOST, port))  # connect to the server
    display = Display()
    # release模块特殊处理
    if options.module == "release" and options.action == "set":
        p = options.src
        if p is None or not os.path.exists(p):
            print("file not exists")
            exit(1)
        f = []
        try:
            f = p.split(os.sep)[1].split(".")
        except IndexError:
            print("file name error")
            exit(1)
        if len(f) == 1:
            options.originSuffix = None
        else:
            options.originSuffix = f[1]
        options.originName = f[0]
        fs = os.path.getsize(p)
        options.size = fs
        cmd = str(options)
        client_socket.send(cmd.encode("utf-8"))  # send msg
        received = client_socket.recv(BUFFER_SIZE).decode()  # receive response
        msg = json.loads(received)
        # debug 服务返回信息
        # print(msg)
        status_code = msg["module"]["module_status"]
        display.display_to_teminal(msg)  # show in terminal
        if status_code < 500:
            fid = msg["module"]["parameter"]["fileId"]
            upload_file(p, fid, options.name, options.tag)

    else:
        cmd = str(options)
        client_socket.send(cmd.encode("utf-8"))  # send msg
        received = client_socket.recv(BUFFER_SIZE).decode()  # receive response
        msg = json.loads(received)
        display.display_to_teminal(msg)  # show in terminal
    client_socket.close()  # close the connection


# 客户端上传文件
def upload_file(path, fid, name, tag):
    url = REGISTRY_URL
    para = {
        "fileId": fid,
        "appName": name,
        "appTag": tag
    }
    file = {"file": open(path, "rb")}
    res = requests.post(url=url, data=para, files=file).text
    info = res.replace("\"", "")
    print(info)


# 终端显示
class Display:
    def __init__(self):
        self.display_mode = "monochrome"  # default display mode

    def display_to_teminal(self, msg):
        if self.display_mode == "monochrome":
            DisplayMonochrome(msg)


class DisplayMonochrome:
    def __init__(self, msg):
        prompt = msg["msg"]
        rows = msg["module"]["display"]
        column_flag = 0
        table = None
        for row in rows:
            if column_flag == 0:
                column_flag = +1
                column_name = row.keys()
                table = PrettyTable(column_name)
            table.add_row(row.values())
        print(prompt)
        print(table)


if __name__ == '__main__':
    client()
