__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import os
import random
import shlex

import tunel.defaults as defaults
import tunel.ssh.commands as commands
import tunel.utils
from tunel.logger import logger
from tunel.settings import Settings


class Tunnel:
    """
    An ssh tunnel provides a route for the user to interact with an application
    This basically enables local port forwarding (called an ss tunnel) using
    the library Paramiko.
    """

    def __init__(self, server, **kwargs):

        # If/when we open a shell
        self.ssh = None
        self.username = None
        self.settings_file = (
            kwargs.get("settings_file") or defaults.default_settings_file
        )
        self.settings = Settings(self.settings_file)
        self.local_port = int(kwargs.get("local_port") or self.settings.local_port)
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

    def execute(self, cmd, login_shell=False, quiet=False, stream=False, xserver=False):
        """
        Execute a command via ssh and a known, named connection.
        """
        if not isinstance(cmd, list):
            cmd = shlex.split(cmd)
        if stream:
            command = ["ssh", "-t", self.server]
        elif xserver:
            command = ["ssh", "-XY", "-o", "ForwardX11=yes", self.server]
        else:
            command = ["ssh", self.server]

        cmd = command + cmd
        return tunel.utils.run_command(cmd, quiet=quiet, stream=stream)

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

    def print_output(self, output, success_code=0, quiet=False):
        """
        Given an output dict, print and color appropriately.
        """
        if output["return_code"] != success_code and output["message"]:
            logger.error(output["message"].strip())
        elif not quiet and output["message"]:
            logger.info(output["message"].strip())

    def execute_or_fail(self, cmd, success_code=0, quiet=False):
        """
        Execute a command, show the command preview, only continue on success.
        """
        output = self.execute(cmd, quiet=quiet)
        if output["return_code"] != success_code:
            logger.exit(output["message"])
        return output["message"].strip()

    def tunnel_login_node(self, port=None, remote_port=None, socket=None, app=None):
        """
        Create a tunnel directly to the login node (e.g., a Singularity app)
        """
        # The app requires a socket
        if app.needs and app.needs.get("socket", False) is True:
            if not socket:
                logger.exit("A socket path is required.")
            return self._tunnel_login_node_socket(socket)

        # The app uses an xserver
        elif app.needs and app.needs.get("xserver", False) is True:
            return self._tunnel_login_node_xserver()

        port = port or self.local_port
        remote_port = remote_port or self.remote_port
        logger.info(
            "Forwarding port %s to %s:%s ..." % (port, self.server, remote_port)
        )
        return self._tunnel_login_node_port()

    def tunnel(
        self,
        machine=None,
        port=None,
        remote_port=None,
        socket=None,
        app=None,
    ):
        """
        Given a remote and local port, open a tunnel. If an isolated node ssh is
        done, the name of the machine is required too.
        """
        # If no machine, we have to do a login node
        if not machine:
            return self._tunnel_login()

        # The app requires a socket
        if app.needs.get("socket", False):
            if not socket:
                logger.exit("A socket path is required.")
            return self._tunnel_isolated_socket(machine, socket=socket)

        port = port or self.local_port
        remote_port = remote_port or self.remote_port
        logger.info(
            "Forwarding port %s to %s:%s ..." % (port, self.server, remote_port)
        )
        return self._tunnel_isolated_port(machine)

    def _get_socket_path(self):
        """
        Get a path for the socket to control the connection. Should be in ~/.ssh
        """
        socket_dir = self.settings.ssh_sockets
        if not os.path.exists(socket_dir):
            os.mkdir(socket_dir)
        return tunel.utils.get_tmpfile(socket_dir, prefix=self.server)

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


# Add tunnel commands to class (only done for organization)

Tunnel._tunnel_wait = commands._tunnel_wait
Tunnel._tunnel_isolated_socket = commands._tunnel_isolated_socket
Tunnel._tunnel_isolated_sockets = commands._tunnel_isolated_sockets
Tunnel._tunnel_isolated_proxyjump_sockets = commands._tunnel_isolated_proxyjump_sockets
Tunnel._tunnel_isolated_port = commands._tunnel_isolated_port
Tunnel._tunnel_login = commands._tunnel_login
Tunnel._tunnel_login_node_port = commands._tunnel_login_node_port
Tunnel._tunnel_login_node_socket = commands._tunnel_login_node_socket
Tunnel._tunnel_login_node_xserver = commands._tunnel_login_node_xserver
