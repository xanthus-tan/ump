# This is a sample Python script.
import os
import signal
import sys
import threading

from src.ump.metadata import config_path
from src.ump.metadata.config import UMPConfig
from src.ump.server.server import ServerCLI, ServerRegistry
from src.ump.utils.logger import logger

VERSION = "UMP 1.2"
if __name__ == '__main__':
    cmd = ""
    try:
        cmd = sys.argv[1]
    except IndexError as error:
        print("执行命令: ump.py start")
        cmd = "start"
    if cmd.lower() == "stop":
        logger.info("stopping ump server")
        config = UMPConfig()
        pid_file = config.get_pid_path()
        with open(pid_file, "r") as f:
            pid = f.readline()
            os.kill(int(pid), signal.SIGINT)
        os.remove(pid_file)
        logger.info("ump server has been stopped.")
        exit(0)
    elif cmd.lower() == "start":
        print("欢迎使用 {} ".format(VERSION))
        logger.info("Initing config info from " + config_path)
        config = UMPConfig()
        server_registry = ServerRegistry(config)
        registry_thread = threading.Thread(target=server_registry.start_registry, daemon=True)
        registry_thread.start()
        server_cli = ServerCLI(config)
        ump_thread = threading.Thread(target=server_cli.run, daemon=True)
        ump_thread.start()
        pid_file = config.get_pid_path()
        with open(pid_file, "w") as f:
            pid = os.getpid()
            f.writelines(str(pid))
        registry_thread.join()
        ump_thread.join()
    else:
        print("Usage: ump.py start || stop")



