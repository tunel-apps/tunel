__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import signal

from tunel.logger import logger

# Shared tunnel functions


def _tunnel_wait(self, socket_file=None):
    """
    Wait for a Control+C to exit and remove a tunnel
    """

    def signal_handler(sig, frame):
        if socket_file:
            self._close_socket(socket_file)
        logger.exit("🛑️ Port forwarding stopped.", return_code=0)

    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl+C")
    signal.pause()


# Tunnel to remote nodes


def _tunnel_isolated_socket(self, machine, socket):
    """
    show commands for 1. isolated socket, and 2. proxyjump.
    """
    self._tunnel_isolated_sockets(machine, socket)
    self._tunnel_isolated_proxyjump_sockets(machine, socket)


def _tunnel_isolated_sockets(self, machine, socket):
    """
    This approach maps a socket first to the login node and connects to it.

    # Running on login node
    $ ssh -NT -L 8888:/tmp/test.sock user@server

    # TWO COMMANDS (and assuming isolated node)
    $ ssh -NT user@server ssh <machine> -NT -L /home/user/login-node.sock:/home/user/path/to/worker-node.sock

    # And another for the local socket
    $ ssh -NT -L <localport>:/home/user/login-node.sock user@server

    # ONE COMMAND
    $ ssh -NT -L <localport>:/home/user/login-node.sock user@server ssh <machine> -NT -L /home/user/login.node.sock:/home/user/path/to/worker-node.sock
    """
    login_node_socket = socket.replace(".sock", ".head-node.sock")
    cmd = [
        "ssh",
        "-NT",
        "-L",
        "%s:%s" % (self.local_port, login_node_socket),
        "%s@%s" % (self.username, self.server),
        "ssh",
        "%s@%s" % (self.username, machine),
        "-NT",
        "-L",
        "%s:%s" % (login_node_socket, socket),
    ]
    logger.c.print()
    logger.c.print("== RUN THIS IN A SEPARATE TERMINAL AFTER THE APP IS READY ==")
    logger.info("%s" % " ".join(cmd))


def _tunnel_isolated_proxyjump_sockets(self, machine, socket):
    """
    This approach uses a proxyjump to only require one socket

    # OR us a proxy
    ssh -J user@server <machine> -NT -L <port>:/home/user/path/to/worker-node.sock
    """
    logger.c.print("== OR (newer ssh) USE A PROXYJUMP ==")
    cmd = [
        "ssh",
        "-J",
        "%s@%s" % (self.username, self.server),
        "%s@%s" % (self.username, machine),
        "-NT",
        "-L",
        "%s:%s" % (self.local_port, socket),
    ]
    logger.info("%s" % " ".join(cmd))


def _tunnel_isolated_port(self, machine):
    """
    Create a tunnel to an isolated node (not tested yet)
    """
    # TODO do we need to close up connections on login node?
    connection = "%s:localhost:%s" % (self.local_port, self.remote_port)
    cmd = [
        "-f",
        "-L",
        connection,
        self.server,
        "ssh",
        "-L",
        connection,
        "-N",
        machine,
    ]
    self.execute(cmd)
    self._tunnel_wait()


# Tunnels to login node


def _tunnel_login(self):
    """
    Create a simple tunnel to the login node (assumes not isolated nodes)
    """
    socket_file = self._get_socket_path()
    cmd = ["-K", "-f", "-M"]

    # Add the socket file
    cmd += ["-S", socket_file, "-L"]
    cmd += ["%s:%s:%s" % (self.local_port, self.server, self.remote_port), "-N"]
    self.execute(cmd)
    self._tunnel_wait(socket_file)


def _tunnel_login_node_socket(self, socket):
    """
    Connect to a login node socket
    """
    cmd = [
        "ssh",
        "-NT",
        "-L",
        "%s:%s" % (self.local_port, socket),
        "%s@%s" % (self.username, self.server),
    ]
    cmd = "%s" % " ".join(cmd)
    logger.info(cmd)


def _tunnel_login_node_xserver(self):
    """
    Connect to a login node via xserver
    """
    cmd = [
        "ssh",
        "-o",
        "ForwardX11=yes",
        "-X",
        "-NT",
        "-L",
        "%s@%s" % (self.username, self.server),
    ]
    cmd = "%s" % " ".join(cmd)
    logger.info(cmd)


def _tunnel_login_node_port(self, machine):
    """
    Create a tunnel to login node port
    TODO this needs testing.
    """
    socket_path = self._get_socket_path()

    # TODO do we need to close up connections on login node?
    connection = "%s:localhost:%s" % (self.local_port, self.remote_port)
    cmd = [
        "-f",
        "-S",
        socket_path,
        "-L",
        connection,
        self.server,
    ]
    self.execute(cmd)
    self._tunnel_wait(socket_path)
