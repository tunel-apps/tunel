__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Original example used to derive this is provided under the MIT License
# https://github.com/akx/uwsgi-socket-example/commit/e5e1df3cdc4a860434b7655663133d8e5103e431

import json
import os
import socket
import struct
import sys


def force_bytes(value):
    """
    Force always returning bytes
    """
    return value if isinstance(value, bytes) else str(value).encode("utf-8")


class ApiResponse:
    def __init__(self, url, raw):
        self.raw = raw
        self.headers = {}
        self.text = ""
        self.parse()

    def parse(self):
        """
        Parse the raw response.
        """
        # headers and content split by two lines
        # Can we use a proper library here?
        headers, content = self.raw.split("\r\n\r\n")
        for header in headers:
            if not header or ":" not in header:
                continue
            k, v = header.split(":", 1)
            self.headers[k.strip()] = v.strip()

        # Raw text
        self.text = content

    def json(self):
        return json.loads(self.text)


class ApiConnection:
    def __init__(self, path, server_name="0.0.0.0", server_port="8000"):
        """
        Create a new tunel API connection.

        Server name and port only matter if your server implements rate limiting
        or other logic to determine if you should be allowed/blocked.
        """
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.path = path
        self.server_name = server_name
        self.server_port = server_port
        if not os.path.exists(path):
            sys.exit("%s does not exist." % path)

    def connect(self):
        self.s.connect(self.path)

    def __exit__(self):
        self.disconnect()

    def disconnect(self):
        self.s.close()

    def send_uwsgi_request(self, header_content):
        """
        Prepare request headers and data, and send.
        """
        data = encode_uwsgi_vars(header_content)
        header = struct.pack(
            "<BHB",
            0,  # modifier1: 0 - WSGI (Python) request
            len(data),  # data size
            0,  # modifier2: 0 - always zero
        )
        self.s.sendall(header)
        self.s.sendall(data)

    def get_response(self, url, width=32):
        """
        Dump the response from the socket.
        """
        # First assemble the content into a string (assumes smaller)
        content = ""
        while True:
            chunk = self.s.recv(width)
            if not chunk:
                break
            content += chunk.decode("ascii", "replace")
        return ApiResponse(url, content)

    def get(self, path):
        """
        Akin to a GET request for a particular path.
        """
        self.connect()
        self.send_uwsgi_request(
            {
                "PATH_INFO": path,
                "REQUEST_METHOD": "GET",
                "SERVER_NAME": self.server_name,
                "SERVER_PORT": self.server_port,
            }.items()
        )
        result = self.get_response(path)
        self.disconnect()
        return result


def encode_uwsgi_vars(values):
    """
    Encode a list of key-value pairs into an uWSGI request header structure.
    """
    # See http://uwsgi-docs.readthedocs.io/en/latest/Protocol.html#the-uwsgi-vars
    buf = []
    for key, value in values:
        key_enc = force_bytes(key)
        val_enc = force_bytes(value)
        buf.append(struct.pack("<H", len(key_enc)))
        buf.append(key_enc)
        buf.append(struct.pack("<H", len(val_enc)))
        buf.append(val_enc)
    return b"".join(buf)
