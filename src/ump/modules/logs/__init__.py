# (c) 2021, xanthus tan <tanxk@neusoft.com>
import select

from exector.remote import RemoteHandler
from src.ump.modules import ActionBase
from src.ump.msg import SUCCESS, FAILED, WARN
from src.ump.metadata.module import HostsModule, DeployModule
from src.ump.utils.ssh import SSH

BUF_SIZE = 1024


# logs模块具体实现
class Action(ActionBase):
    def get(self, instruction):
        sid = instruction["insid"]
        if sid is None or sid == "":
            self.response.set_display([{"Error": "not found instance id"}])
            return
        dm = DeployModule()
        host_and_group = dm.get_instance_group_and_host(sid)
        host = host_and_group["host"]
        group = host_and_group["group"]
        hm = HostsModule()
        host_info = hm.get_host_info(group_id=group, host_ip=host)
        ssh = SSH(host_info["addr"], host_info["port"], host_info["username"], host_info["password"])
        ssh_handler = ssh.connect_server()
        transport = ssh_handler.get_transport()
        transport.set_keepalive(1)
        channel = transport.open_session()
        log_path = dm.get_app_log_path(sid)
        cmd = "tail -f " + log_path
        channel.settimeout(1)
        channel.exec_command(cmd)
        LeftOver = ""
        while transport.is_active():
            rl, wl, xl = select.select([channel], [], [], 0.0)
            if len(rl) > 0:
                buf = channel.recv(BUF_SIZE)
                if len(buf) > 0:
                    lines_to_process = LeftOver + str(buf)
                    EOL = lines_to_process.rfind("\n")
                    if EOL != len(lines_to_process) - 1:
                        LeftOver = lines_to_process[EOL + 1:]
                        lines_to_process = lines_to_process[:EOL]
                    else:
                        LeftOver = ""
                    for line in lines_to_process.splitlines():
                        if "error" in line:
                            print(line)
                        print(line)
        ssh_handler.close()



                # stdin, stdout, stderr = ssh_handler.exec_command("cat  " + log_path)
        # print(stdout.read())
        # msg = stdout.read().decode().strip()
        # print(msg)
        
    def set(self, instruction):
        pass

    def delete(self, instruction):
        pass
