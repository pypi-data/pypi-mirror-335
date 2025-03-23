from configparser import ConfigParser
import os

class ConfigSaver:
    def __init__(self, logger, config_file_path, profile, host, port, user, open_ports, close_ports):
        self.config_file_path = os.path.expanduser(config_file_path)
        self.profile = profile
        self.host = host
        self.port = port
        self.user = user
        self.open_ports = open_ports
        self.close_ports = close_ports
        self.logger = logger

    def save(self):
        config = ConfigParser()
        config.read(self.config_file_path)
        if self.profile in config:
            self.logger.debug(f"Found existing configuration")
            self._update_existing_profile(config)
        else:
            self.logger.debug(f"Create new profile")
            self._create_new_profile(config)

        with open(self.config_file_path, 'w') as f:
            config.write(f)
        self.logger.debug(f"Configuration saved to {self.config_file_path}")

    def _update_existing_profile(self, config):
        profile = config[self.profile]
        profile["host"] = self.host or profile.get("host")
        profile["ssh_port"] = self.port or profile.get("ssh_port")
        profile["user"] = self.user or profile.get("user")
        profile["open_ports"] = self.open_ports or profile.get("open_ports")
        profile["close_ports"] = self.close_ports or profile.get("close_ports")

    def _create_new_profile(self, config):
        config[self.profile] = {
            "host": str(self.host),
            "ssh_port": self.port or str(22),
            "user": self.user or "user",
            "open_ports": str(self.open_ports),
            "close_ports": str(self.close_ports)
        }
        self.logger.debug(f"Created new profile '{self.profile}'")
