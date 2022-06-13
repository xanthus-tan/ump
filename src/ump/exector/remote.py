# (c) 2021, xanthus tan <tanxk@neusoft.com>
import socket

from paramiko.ssh_exception import SSHException
from sqlalchemy.sql import select

from src.ump.modules.hosts.model import UmpHostsInfo, HOST_ONLINE
from src.ump.utils import current_time_str
from src.ump.utils.dbutils import DB
from src.ump.utils.logger import logger
from src.ump.utils.ssh import SSH, SFTP


# 远程连接类
class Connector:

    def __init__(self):
        self.db = DB()
        self.hosts = []
        self.ssh_pool = []

    def get_ssh_pool(self, group):
        s = select(UmpHostsInfo).where(UmpHostsInfo.status == HOST_ONLINE, UmpHostsInfo.group_id == group)
        conn = self.db.get_connect()
        rs = conn.execute(s)
        for r in rs:
            ssh = SSH(r.address, 22, r.login_username, r.login_password)
            self.ssh_pool.append(ssh)
        conn.close()
        return self.ssh_pool

    def close_ssh_connect(self):
        for ssh in self.ssh_pool:
            ssh.ssh_client.close()


# 远程执行命令
class RemoteHandler:
    def __init__(self, timeout=2):
        self.timeout = timeout

    # 执行SSH远程命令
    def remote_shell(self, ssh_pool: [], cmd):
        v = []
        failed_hosts = []
        for ssh in ssh_pool:
            try:
                c = ssh.connect_server(self.timeout)
                stdin, stdout, stderr = c.exec_command(cmd)
                msg = stdout.read().decode().strip()
                j = {"out": msg,
                     "time": current_time_str(),
                     "host": ssh.get_address()
                     }
                v.append(j)
                logger.debug("Host " + ssh.get_address() + " is running " + cmd)
            except SSHException:
                logger.error(ssh.get_address() + "'s ssh session not active")
                failed_hosts.append(ssh.get_address())
            except AttributeError:
                logger.error(ssh.get_address() + "'not open_session, cause by object has no attribute open_session")
                failed_hosts.append(ssh.get_address())
            except socket.timeout:
                logger.error(ssh.get_address() + "'s ssh connect time out")
                failed_hosts.append(ssh.get_address())
                continue
        return v, failed_hosts

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


