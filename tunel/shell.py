__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


import paramiko
from paramiko.py3compat import u
import socket
import sys

try:
    import select
    import termios
    import tty
except ImportError:
    pass


def posix(channel):
    """
    Create an interactive posix shell
    https://github.com/paramiko/paramiko/blob/main/demos/interactive.py
    """
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        channel.settimeout(0.0)

        while True:
            r, w, e = select.select([channel, sys.stdin], [], [])
            if channel in r:
                try:
                    data = u(channel.recv(1024))
                    if len(data) == 0:
                        sys.stdout.write("\r\n👋️ Bye!\r\n")
                        break
                    sys.stdout.write(data)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                data = sys.stdin.read(1)
                if len(data) == 0:
                    break
                channel.send(data)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


def windows(channel):
    """
    Create an interactive windows shell
    https://github.com/paramiko/paramiko/blob/main/demos/interactive.py
    """
    import threading

    sys.stdout.write(
        "Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n"
    )

    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write("\r\n*** EOF ***\r\n\r\n")
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(channel,))
    writer.start()

    try:
        while True:
            data = sys.stdin.read(1)
            if not data:
                break
            channel.send(data)
    except EOFError:
        # user hit ^Z or F6
        pass
