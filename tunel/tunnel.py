__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from tunel.logger import logger
import tunel.tunnel
import getpass
import os
import random
import re
import paramiko
import socket
import select
import sys

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer


def forward_tunnel(local_port, remote_host, remote_port, transport):
    """
    The function to call to init a port forwarding session.
    """

    class ForwardHander(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport

    ForwardServer(("", local_port), ForwardHander).serve_forever()


class ForwardServer(SocketServer.ThreadingTCPServer):
    """
    A forwarding server, akin to vsoch/forward
    """

    daemon_threads = True
    allow_reuse_address = True


class Handler(SocketServer.BaseRequestHandler):
    """
    Handler for forward
    https://github.com/paramiko/paramiko/blob/main/demos/forward.py
    """

    def handle(self):
        channel = None
        try:
            channel = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.chain_host, self.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            logger.error(
                "😭️ Incoming request to %s:%s failed: %s"
                % (self.chain_host, self.chain_port, repr(e))
            )
            return
        if channel is None:
            logger.error(
                "😭️ Incoming request to %s:%s was rejected by the SSH server."
                % (self.chain_host, self.chain_port)
            )
            return

        logger.info(
            "😹️ Connected!  Tunnel open %r -> %r -> %r"
            % (
                self.request.getpeername(),
                channel.getpeername(),
                (self.chain_host, self.chain_port),
            )
        )
        while True:
            r, w, x = select.select([self.request, channel], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                channel.send(data)
            if channel in r:
                data = channel.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        channel.close()
        self.request.close()
        logger.info("Tunnel closed from %r" % (peername,))
