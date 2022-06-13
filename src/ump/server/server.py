# (c) 2021, xanthus tan <tanxk@neusoft.com>
import json
import os
import socketserver
import threading

from src.ump.metadata import ump_home
from src.ump.metadata.config import UMPConfig
from src.ump.processor.swtich import InstructionHandler
from src.ump.server.translate import CLITranslate
from src.ump.utils.logger import logger
from . import Command
from .flask.registry import registry_app

# 共享ump配置信息对象
ump_config = None


# server interface
class ServerCLI(Command):
    def __init__(self, config: UMPConfig):
        self.config = config

    def run(self):
        global ump_config
        ump_config = self.config
        port = self.config.get_cli_listener_port()
        with ThreadedTCPServer(('', port), CLIHandler) as server:
            logger.info('The ump cli server is running, port is ' + str(port))
            server.serve_forever()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


class CLIHandler(socketserver.StreamRequestHandler):
    def handle(self):
        client = f'{self.client_address} on {threading.currentThread().getName()}'
        logger.info(f'Connected: {client}')
        translate = CLITranslate()
        handler = InstructionHandler(ump_config)
        while True:
            cmd = self.request.recv(1024)
            if not cmd:
                break
            msg = handler.run(cmd.decode('utf-8'), translate)
            client_msg = json.dumps(msg)
            self.wfile.write(client_msg.encode('utf-8'))
        logger.info(f'Closed: {client}')


class ServerRegistry:
    def __init__(self, config):
        self.config = config
        # 缓存大小，单位MB

    def start_registry(self):
        p = self.config.get_registry_path()
        if p == "registry":
            registry_base = os.path.join(ump_home, p)
        else:
            registry_base = p
        if not os.path.exists(registry_base):
            os.makedirs(registry_base)
        tmp = os.path.join(registry_base, "_tmp")
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        port = self.config.get_registry_port()
        listener = self.config.get_registry_bind()
        logger.info("The registry server has been started, port is " + str(port))
        registry_app.registry_base = registry_base
        registry_app.run(host=listener,
                         port=port,
                         debug=True,
                         use_reloader=False)
