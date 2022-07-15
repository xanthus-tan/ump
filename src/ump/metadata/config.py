# (c) 2021, xanthus tan <tanxk@neusoft.com>
import logging
import os

from src.ump.metadata import ump_home, ump_config_yaml
from src.ump.utils.file import is_linux_drive_letter, is_windows_drive_letter

DEFAULT_PORT = 3003


class UMPConfig:
    def __init__(self):
        self.ump = ump_config_yaml()

    def get_root_dir_name(self):
        return self.ump["node"]["root_dir_name"]

    def get_registry_path(self):
        return os.path.join(ump_home, self.ump["registry"]["path"])

    def get_registry_tmp_path(self):
        return os.path.join(ump_home, self.ump["registry"]["path"], "_tmp")

    def get_registry_port(self):
        return int(self.ump["registry"]["port"])

    def get_registry_bind(self):
        return self.ump["registry"]["bind"]

    def get_registry_size_limit(self):
        return int(self.ump["registry"]["file_size_limit"])

    def get_health_interval(self):
        return int(self.ump["health"]["interval"])

    def get_collector_path(self):
        return os.path.join(ump_home, self.ump["monitor"]["tool"]["path"])

    def get_metrics_to_file_enable_status(self):
        return str(self.ump["monitor"]["persistence"]["file"]["enable"])

    def get_metrics_to_file_path(self):
        return os.path.join(ump_home, self.ump["monitor"]["persistence"]["file"]["path"])

    def get_metrics_to_es_enable_status(self):
        return str(self.ump["monitor"]["persistence"]["elasticsearch"]["enable"])

    def get_metrics_to_es_url(self):
        es_url = self.ump["monitor"]["persistence"]["elasticsearch"]["url"]
        if es_url is None:
            es_url = ""
        return es_url

    def get_metrics_to_es_username(self):
        es_username = self.ump["monitor"]["persistence"]["elasticsearch"]["username"]
        if es_username is None:
            es_username = ""
        return es_username

    def get_metrics_to_es_password(self):
        es_pwd = self.ump["monitor"]["persistence"]["elasticsearch"]["password"]
        if es_pwd is None:
            es_pwd = ""
        return es_pwd

    def get_metrics_to_es_cert_path(self):
        cert_path = self.ump["monitor"]["persistence"]["elasticsearch"]["cert"]
        if cert_path is None:
            cert_path = ""
        return os.path.join(ump_home, cert_path)

    def get_ssh_timeout(self):
        return int(self.ump["ssh"]["timeout"])

    def get_ssh_default_port(self):
        return self.ump["ssh"]["port"]

    def get_pid_path(self):
        return os.path.join(ump_home, self.ump["server"]["pid"]["path"])

    def get_cli_listener_port(self):
        port = int(self.ump["server"]["port"])
        if port is None or str(port) == "":
            port = DEFAULT_PORT
        return int(port)


class LoggerConfig:
    def __init__(self):
        self.ump = ump_config_yaml()

    def get_log_level(self):
        level = self.ump["server"]["logs"]["level"].lower()
        if level == "info":
            level = logging.INFO
        elif level == "warn":
            level = logging.WARNING
        elif level == "debug":
            level = logging.DEBUG
        elif level == "error":
            level = logging.ERROR
        else:
            level = logging.INFO
        return level

    def get_log_handler(self):
        handler = self.ump["server"]["logs"]["handler"].lower()
        if handler == "file":
            return handler
        return "console"

    def get_log_path(self):
        log_path = self.ump["server"]["logs"]["path"].lower()
        if len(log_path) == 1 and log_path == "/":
            return log_path
        if not is_linux_drive_letter(log_path[0]) and not is_windows_drive_letter(log_path[:2]):
            return os.path.join(ump_home, log_path)
        return log_path
