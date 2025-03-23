from argparse import ArgumentParser, RawDescriptionHelpFormatter, SUPPRESS
from .config_loader import ConfigLoader
from .config_saver import ConfigSaver
from .logger_singleton import init_logger
from .command_executor import CommandExecutor
import shutil
import sys

def create_parser() -> ArgumentParser:
    example_usage = """
Example Usage:

\t$ knockssh
\t$ knockssh -p another_profile
\t$ knockssh -p myserver -H 1.2.3.4 -U user -O 7000,8000 -C 8000,7000
\t$ knockssh --save -p new_profile --host myserver.com --port 2222 --user user --open-ports 1234,2345 --close-ports 2345,1234
\t$ knockssh --save -p another_server -H changed-hosd.org
    """

    parser = ArgumentParser(
           prog="knockssh"
           , description = "knockssh is a wrapper around knock and"
          + " ssh, which enables you to use this combination more easily."
          , epilog = example_usage
          , formatter_class = RawDescriptionHelpFormatter
          )

    parser.add_argument("-s", "--save", action="store_true", help="Save/update the specified profile in the config file, then exit")
    parser.add_argument("-p", "--profile", default="default", help="Profile name to use or update (default: 'default')")
    parser.add_argument("-H", "--host", help="Override or set the host")
    parser.add_argument("-U", "--user", help="Override or set the user name (default: 'user')")
    parser.add_argument("-P", "--port", help="Override or set the SSH port (default: 22)")
    parser.add_argument("-O", "--open-ports", help="Comma-separated ports to knock for opening")
    parser.add_argument("-C", "--close-ports", help="Comma-separated ports to knock for closing")
    parser.add_argument("-f", "--config-file", default="~/.knockssh.conf", help="Specify an alternative config file (default: ~/.knockssh.conf)")
    parser.add_argument("-v", "--verbose", default=0, action="count")
    parser.add_argument("--generate-manpage", action="store_true", help=SUPPRESS)

    return parser

def execute_knock(config, executor, ports_key, success_msg):
    ports = config[ports_key].split(',')
    command = ["knock", "-v", config["host"], *ports]
    executor.run(command, success_msg)

def execute_ssh(config, executor):
    command = ["ssh", "-p", str(config["port"]), f"{config['user']}@{config['host']}"]
    result = executor.run(command, "SSH connection successful.", check=False)
    if result.returncode != 0:
        executor.logger.info(f"SSH session ended with exit code {result.returncode}.")

def execute_knock_open(config, executor):
    execute_knock(config, executor, "open_ports", "Ports opened successfully.")

def execute_knock_close(config, executor):
    execute_knock(config, executor, "close_ports", "Ports closed successfully.")

def main():
    if not all(shutil.which(cmd) for cmd in ["knock", "ssh"]):
        sys.exit("This program requires both 'knock'and 'ssh' packages to be installed")

    parser = create_parser()
    args = parser.parse_args()

    logger = init_logger(args.verbose)
    logger.debug(f"Arguments parsed: {args}")

    logger.debug(f"Config file set to: {args.config_file}")

    arg_values = {
        "config_file_path": args.config_file,
        "profile": args.profile,
        "host": args.host,
        "port": args.port,
        "user": args.user,
        "open_ports": args.open_ports,
        "close_ports": args.close_ports,
    }

    if args.save:
        logger.info(f"Saving profile '{args.profile}'...")
        config_saver = ConfigSaver(logger, **arg_values
        )
        try:
            config_saver.save()
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
        return

    logger.info(f"Loading configuration for profile '{args.profile}'...")
    config_loader = ConfigLoader(logger, **arg_values)
    try:
        config = config_loader.load()
        logger.info(f"Configuration loaded: {config}")
    except ValueError as e:
        logger.error(f"Configuration load failed: {e}")
        return

    executor = CommandExecutor(logger)
    logger.debug("Executing knock open...")
    execute_knock_open(config, executor)

    logger.debug("Executing SSH connection...")
    execute_ssh(config, executor)

    logger.debug("Executing knock close...")
    execute_knock_close(config, executor)

if __name__ == "__main__":
    main()
