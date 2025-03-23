# knockssh

**knockssh** is a simple wrapper around [`ssh`](https://man.openbsd.org/ssh.1) and [`knock`](https://github.com/jvinet/knock), aimed at making the port-knocking workflow more convenient. 
It helps ensure your ports remain secure by reliably executing knock sequences before and after SSH sessions, so you'll never leave ports exposed by mistake.

## Installation
### Manual Installation from Source (Recommended)

The recommended approach is to install **knockssh** directly from source:

```bash
git clone https://git.andreasglashauser.com/git/knockssh.git
cd knockssh
pip install .
```
### Install from PyPI
**knockssh** is published on [PyPI](https://pypi.org/project/knockssh/).  

To install the latest release:
```bash
pip install knockssh
```
After installation, you can run:

```bash
knockssh --help
```

## Usage
Once installed, you can use `knockssh` to manage your SSH connections with integrated port-knocking.  
It uses a configuration file (default: `~/.knockssh.conf`) to store connection profiles, but you can override everything via command-line options.

### Command-Line Options
```
-s, --save             Save or update the specified profile in the config file and exit
-p, --profile NAME     Profile name to use or update (default: 'default')
-H, --host HOST        Override or set the host
-U, --user USER        Override or set the user name (default: 'user')
-P, --port PORT        Override or set the SSH port (default: 22)
-O, --open-ports PORTS Comma-separated ports to knock for opening
-C, --close-ports PORTS Comma-separated ports to knock for closing
-f, --config-file FILE Path to alternative config file (default: ~/.knockssh.conf)
-v, --verbose          Increase verbosity (use multiple times for more detail)
```

## Examples
### Basic SSH Connection with Port Knocking

If you have a profile already defined:

```bash
knockssh
```

This will:
- Load the default profile from the config file
- Execute the "open" knock sequence
- Initiate the SSH connection
- Execute the "close" knock sequence after the SSH session ends

### Using a Specific Profile
```bash
knockssh -p another_profile
```

Loads and uses the `another_profile` entry from the config.

### Direct Connection Parameters (No Profile)
```bash
knockssh -p myserver -H 1.2.3.4 -U user -O 7000,8000 -C 8000,7000
```

This will:
- Use `myserver` as the temporary profile name
- Connect to `1.2.3.4` with user `user`
- Knock ports 7000, 8000 to open
- SSH to the host
- Knock ports 8000, 7000 to close

### Saving a New Profile
```bash
knockssh --save -p new_profile --host myserver.com --ssh-port 2222 --user user --open-ports 1234,2345 --close-ports 2345,1234
```

This saves the given settings into the config file under `new_profile`. No SSH connection will be started.

### Updating an Existing Profile
```bash
knockssh --save -p another_server -H changed-host.com
```

This updates just the host of the `another_server` profile.

If you encounter any issues, have questions, or require further clarification, feel free to contact me. Happy knocking!
