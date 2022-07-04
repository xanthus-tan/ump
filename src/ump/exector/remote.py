# (c) 2021, xanthus tan <tanxk@neusoft.com>
import socket

from paramiko.ssh_exception import SSHException

from src.ump.modules.hosts.meta import HostsMetaInstance
from src.ump.utils import current_time_str
from src.ump.utils.logger import logger
from src.ump.utils.ssh import SSH, SFTP


# 远程连接类
class Connector:
    def __init__(self):
        self.ssh_pool = []

    def get_ssh_pool(self, group):
        hostsMeta = HostsMetaInstance()
        hosts = hostsMeta.get_host_online_info(group)
        self.ssh_pool = self.get_ssh_list(hosts)
        return self.ssh_pool

    def get_ssh_list(self, hosts: []):
        ssh_list = []
        for h in hosts:
            ssh = SSH(h["addr"], h["port"], h["username"], h["password"])
            ssh_list.append(ssh)
        return ssh_list

    def close_ssh_connect(self):
        for ssh in self.ssh_pool:
            ssh.ssh_client.close()


# 远程执行命令
class RemoteHandler:
    def __init__(self, timeout=2):
        self.timeout = timeout

    # 执行SSH远程命令
    def remote_shell(self, ssh_pool: [], cmd):
        success = []
        failed = []
        for ssh in ssh_pool:
            try:
                c = ssh.connect_server(self.timeout)
                stdin, stdout, stderr = c.exec_command(cmd)
                msg = stdout.read().decode().strip()
                j = {"out": msg,
                     "time": current_time_str(),
                     "host": ssh.get_address()
                     }
                success.append(j)
                logger.debug("Host " + ssh.get_address() + " is running " + cmd)
            except SSHException:
                logger.error(ssh.get_address() + "'s ssh session not active")
                failed.append(ssh.get_address())
            except AttributeError:
                logger.error(ssh.get_address() + "'not open_session, cause by object has no attribute open_session")
                failed.append(ssh.get_address())
            except socket.timeout:
                logger.error(ssh.get_address() + "'s ssh connect time out")
                failed.append(ssh.get_address())
                continue
        return success, failed

    # 远程部署文件
    def remote_copy(self, ssh_pool: [], src, des):
        success = []
        failed = []
        for ssh in ssh_pool:
            try:
                ssh_connect = ssh.connect_server()
                sftp = SFTP(ssh_connect)
                sftp.put_file(src, des)
                success.append(ssh.get_address())
            except FileNotFoundError as error:
                logger.error(ssh.get_address() + " 可能是权限问题无法访问或者没有该路径 " + error.__str__())
                failed.append(ssh.get_address())
            except socket.timeout as error:
                logger.error(error.__str__() + " in " + ssh.get_address())
                logger.error(ssh.get_address() + " 无法远程连接,请检查主机！")
                failed.append(ssh.get_address())
        return success, failed


