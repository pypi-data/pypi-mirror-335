from configparser import ConfigParser
from typing import Dict, Union
import os

class ConfigLoader:
    def __init__(self, logger, config_file_path, profile, host, port, user, open_ports, close_ports):
        self.config_file_path = os.path.expanduser(config_file_path)
        self.profile = profile
        self.logger = logger
        self.host = host
        self.port = port
        self.user = user
        self.open_ports = open_ports
        self.close_ports = close_ports

    def load(self) -> Dict[str, Union[str, int]]:
        config = ConfigParser()
        config.read(self.config_file_path)

        if self.profile not in config:
            raise ValueError(f"Profile '{self.profile}' not found in config file.")

        self.logger.debug(f"Loaded profile '{self.profile}' from config file.")

        return {
            "host": self.host or config[self.profile]["host"],
            "port": self.port or config[self.profile]["ssh_port"],
            "user": self.user or config[self.profile]["user"],
            "open_ports": self.open_ports or config[self.profile]["open_ports"],
            "close_ports": self.close_ports or config[self.profile]["close_ports"]
        }
