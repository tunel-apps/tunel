__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from .settings import Settings
import tunel.defaults as defaults
from tunel.logger import logger
import tunel.tunnel
import tunel.shell
import random
import re
import paramiko

try:
    import termios

    has_termios = True
except ImportError:
    has_termios = False


class Tunnel:
    """
    A tunel tunnel provides a route for the user to interact with an application
    This basically enables local port forwarding (called an ss tunnel) using
    the library Paramiko.
    """

    def __init__(self, server, **kwargs):

        # If/when we open a shell
        self.ssh = None

        self.settings_file = (
            kwargs.get("settings_file") or defaults.default_settings_file
        )
        self.settings = Settings(self.settings_file)
        self.local_port = int(kwargs.get("local_port") or self.settings.local_port)
        self.isolated_nodes = (
            kwargs.get("isolated_nodes") or self.settings.isolated_nodes
        )
        self.remote_port = int(
            kwargs.get("remote_port")
            or self.settings.remote_port
            or self._random_port()
        )

        # Local port to forward to
        self.web_port = kwargs.get("web_port") or self.settings.web_port

        # Save the name of the server to connect to
        self.server = server

    def __del__(self):
        if self.ssh:
            self.ssh.close()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[tunel-ssh]"

    def _random_port(self):
        """
        Generate a random port for an ssh session
        """
        return random.choice(range(self.settings.min_port, self.settings.max_port))

    def connect(self):
        """
        Connect via ssh
        """
        # Don't connect again if we already have
        if self.ssh:
            return

        self.config = paramiko.SSHConfig()
        self.config.parse(open(self.settings.ssh_config))
        if self.server not in self.config.get_hostnames():
            logger.exit(
                "%s is not configured in known hostnames of %s"
                % (self.server, self.settings.ssh_config)
            )

        # rename user to username so the params match
        self.params = self.config.lookup(self.server)
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            self.params["hostname"],
            port=int(self.params["port"]),
            username=self.params["user"],
            password=self.params.get("password"),
        )

    def shell(self):
        """
        Connect to a server via standard ssh
        """
        self.connect()
        channel = self.ssh.invoke_shell()
        if has_termios:
            tunel.shell.posix(channel)
        else:
            tunel.shell.windows(channel)
        # os.system("ssh %s" % self.server)

    def _prepare_command(self, cmd):
        """
        Prepare the command to be used by the client
        """
        if cmd and isinstance(cmd, list):
            return " ".join(cmd).strip("\n")
        elif cmd:
            return cmd.strip("\n")
        return cmd

    def tunnel(self):
        """
        Given a remote and local port, open a tunnel.
        """
        self.connect()
        logger.info(
            "Forwarding port %s to %s:%s ..."
            % (self.local_port, self.server, self.remote_port)
        )

        try:
            tunel.tunnel.forward_tunnel(
                self.local_port, self.server, self.remote_port, self.ssh.get_transport()
            )
        except KeyboardInterrupt:
            logger.info("🛑️ Port forwarding stopped.")

    def _clean_line(self, line):
        """
        Clean up an output line of coloring and formatting special characters
        """
        regex = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
        line = regex.sub("", line)
        for char in ["\b", "\r", "\n"]:
            line = line.replace(char, "")
        return line

    @property
    def _finish_line(self):
        return "Done! Finished with exit status"

    @property
    def _echo_cmd(self):
        return "echo {} $?".format(self._finish_line)

    def print_output(self, output, success_code=0):
        """
        Given an output dict, print and color appropriately.
        """
        if output["exit_status"] != success_code:
            logger.error("\n".join(output["err"]))
        else:
            logger.info("\n".join(output["out"]))

    def execute_or_fail(self, cmd, success_code=0):
        """
        Execute a command, show the command preview, only continue on success.
        """
        cmd = self._prepare_command(cmd)
        logger.info(cmd)
        output = self.execute(cmd)
        if output["exit_status"] != success_code:
            logger.exit("\n".join(output["err"]))
        return output["out"]

    def execute(self, cmd):
        """
        connect and then execute a command - a more controlled interaction
        """
        if not cmd:
            logger.warning("You must provide a command to execute.")
            return

        self.connect()
        cmd = self._prepare_command(cmd)
        channel = self.ssh.invoke_shell()

        self.stdin = channel.makefile("wb")
        self.stdout = channel.makefile("r")
        self.stdin.write(cmd + "\n")
        self.stdin.write(self._echo_cmd + "\n")
        self.stdin.flush()

        output = {"out": [], "err": [], "exit_status": 0}
        for line in self.stdout:

            # Ensure line is a string
            strline = str(line)

            if strline.startswith(cmd) or strline.startswith(self._echo_cmd):
                output["out"] = []

            # Exit status should be on last finish line
            elif strline.startswith(self._finish_line):
                output["exit_status"] = int(strline.rsplit(maxsplit=1)[1])
                if output["exit_status"]:
                    # stderr is combined with stdout.
                    # thus, swap sherr with shout in a case of failure.
                    output["err"] = output["out"]
                    output["out"] = []
                break
            else:
                # get rid of 'coloring and formatting' special characters
                output["out"].append(self._clean_line(line))

        # Clean up echo / prompt from output and error
        for key in ["out", "err"]:
            if output[key] and self._echo_cmd in output[key][-1]:
                output[key].pop()
            if output[key] and cmd in output[key][-1]:
                output[key].pop(0)

        return output
