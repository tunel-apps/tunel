__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from .settings import Settings
import tunel.defaults as defaults
from tunel.logger import logger
import tunel.utils
import getpass
import random
import re
import os
import signal
import shlex
import subprocess


class Tunnel:
    """
    An ssh tunnel provides a route for the user to interact with an application
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

    def _random_port(self):
        """
        Generate a random port for an ssh session
        """
        return random.choice(range(self.settings.min_port, self.settings.max_port))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[tunel-ssh]"

    def execute(self, cmd, login_shell=False):
        """
        Execute a command via ssh and a known, named connection.
        """
        if not isinstance(cmd, list):
            cmd = shlex.split(cmd)
        cmd = ["ssh", self.server] + cmd
        return tunel.utils.run_command(cmd)

    def scp_to(self, src, dest):
        """
        Copy a file onto the server
        """
        self.execute_or_fail("mkdir -p %s" % os.path.dirname(dest))
        cmd = ["scp", src, "%s:%s" % (self.server, dest)]
        return tunel.utils.run_command(cmd)

    def scp_from(self, src, dest):
        """
        Copy a file from the server to local
        """
        cmd = ["scp", "%s:%s" % (self.server, src), dest]
        return tunel.utils.run_command(cmd)

    def print_output(self, output, success_code=0):
        """
        Given an output dict, print and color appropriately.
        """
        if output["return_code"] != success_code:
            logger.error(output["message"].strip())
        else:
            print(output["message"].strip())

    def execute_or_fail(self, cmd, success_code=0):
        """
        Execute a command, show the command preview, only continue on success.
        """
        output = self.execute(cmd)
        if output["return_code"] != success_code:
            logger.exit(output["message"])
        return output["message"].strip()

    def tunnel(self, machine=None, port=None, remote_port=None):
        """
        Given a remote and local port, open a tunnel. If an isolated node ssh is
        done, the name of the machine is required too.
        """
        port = port or self.local_port
        remote_port = remote_port or self.remote_port
        logger.info(
            "Forwarding port %s to %s:%s ..." % (port, self.server, remote_port)
        )

        if self.settings.isolated_nodes:
            if not machine:
                logger.exit("A machine is required to forward to.")
            self._tunnel_isolated(machine)
        else:
            self._tunnel_login()

    def _get_socket_path(self):
        """
        Get a path for the socket to control the connection. Should be in ~/.ssh
        """
        socket_dir = self.settings.ssh_sockets
        if not os.path.exists(socket_dir):
            os.mkdir(socket_dir)
        return tunel.utils.get_tmpfile(socket_dir, prefix=self.server)

    def _tunnel_login(self):
        """
        Create a simple tunnel to the login node (assumes not isolated nodes)
        """
        socket_file = self._get_socket_path()
        cmd = [
            "-K",
            "-f",
            "-M",
            "-S",
            socket_file,
            "-L",
            "%s:%s:%s" % (self.local_port, self.server, self.remote_port),
            "-N",
        ]
        res = self.execute(cmd)
        self._tunnel_wait(socket_file)

    def _tunnel_wait(self, socket_file):
        """
        Wait for a Control+C to exit and remove a tunnel
        """

        def signal_handler(sig, frame):
            self._close_socket(socket_file)
            logger.exit("🛑️ Port forwarding stopped.", return_code=0)

        signal.signal(signal.SIGINT, signal_handler)
        print("Press Ctrl+C")
        signal.pause()

    def _close_socket(self, socket_file):
        """
        Ensure an ssh socket is closed
        """
        cmd = ["-S", socket_file, "-O", "exit", self.server]
        try:
            self.execute(cmd)
        except:
            pass
        if os.path.exists(socket_file):
            os.remove(socket_file)

    def _tunnel_isolated(self, machine):
        """
        Create a tunnel to an isolated node (not tested yet)
        """
        socket_file = self._get_socket_path()

        # TODO do we need to close up connections on login node?
        connection = "%s:localhost:%s" % (self.local_port, self.remote_port)
        cmd = [
            "-f",
            "-S",
            socket_path,
            "-L",
            connection,
            self.server,
            "ssh",
            "-L",
            connection,
            "-N",
            machine,
        ]
        res = self.execute(cmd)
        self._tunnel_wait(socket_file)

    def shell(self, cmd=None, interactive=False):
        """
        Pass the process over to shell
        """
        command = "ssh %s" % self.server
        if interactive:
            command = "ssh -t %s" % self.server
        if cmd:
            command = "%s %s" % (command, cmd)
        os.system(command)
        logger.info("👋️ Goodbye!")
