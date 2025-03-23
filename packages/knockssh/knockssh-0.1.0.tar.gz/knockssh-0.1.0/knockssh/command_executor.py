import subprocess

class CommandExecutor:
    def __init__(self, logger):
        self.logger = logger

    def run(self, command, success_message, check=True):
        self.logger.debug(f"Running command: {command}")
        result = subprocess.run(command, check=check)
        if check:
            self.logger.info(success_message)
        return result
