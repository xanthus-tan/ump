# (c) 2021, xanthus tan <tanxk@neusoft.com>
import os
import time

import paramiko

from src.ump.utils.logger import logger


# ssh连接工具
class SSH:

    def __init__(self, server, port, user, pwd):
        paramiko.SSHClient.address = ""
        self.ssh_client = paramiko.SSHClient()
        self.server = server
        self.port = port
        self.user = user
        self.pwd = pwd

    # 连接远程服务器
    def connect_server(self, timeout=2):
        # create ssh client
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client = self._connect(timeout)
        return self.ssh_client

    # 重新连接远程服务器
    def retry_server(self):
        self.ssh_client = self._connect(timeout=1)
        return self.ssh_client

    # 服务器连接方法
    def _connect(self, timeout):
        try:
            self.ssh_client.connect(self.server, self.port, self.user, self.pwd, timeout=timeout)
        except TimeoutError:
            logger.error("由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。")
        logger.info(self.server + " connection established successfully")
        return self.ssh_client

    def get_address(self):
        return self.server

    def close(self):
        self.ssh_client.close()


class SFTP:
    def __init__(self, ssh):
        self.ssh = ssh
        self.sftp = ssh.open_sftp()

    def put(self, local_path, remote_path):
        if os.path.isfile(local_path):
            self._upload_file(local_path, remote_path)
        else:
            current_dir = local_path.split(os.sep)[-1]
            remote_path = remote_path + "/" + current_dir
            self.ssh.exec_command("mkdir -p " + remote_path)
            file_list = os.listdir(local_path)
            for file in file_list:
                sub_path = os.path.join(local_path, file)
                if os.path.isfile(sub_path):
                    time.sleep(0.03)
                    self._upload_file(sub_path, remote_path)
                else:
                    self.put(sub_path, remote_path)

    def _upload_file(self, local_path, remote_path):
        filename = os.path.basename(local_path)
        self.sftp.put(local_path, remote_path + "/" + filename)

    def put_file(self, src_file, remote_file):
        # s = remote_file
        # remote_path = s[:s.rfind("/")]
        # try:
        #     self.ssh.exec_command("mkdir -p " + remote_path)
        # except SSHException as error:
        #     print(error)
        self.sftp.put(src_file, remote_file)

    def get_file(self, remote_path, local_path):
        try:
            self.sftp.stat(remote_path)
            self.sftp.get(remote_path, local_path)
        except IOError:
            logger.info("remote file not exist")


