__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import shlex
import time

from tunel.logger import logger

from .container import ContainerLauncher


class Singularity(ContainerLauncher):
    name = "singularity"

    def run(self, *args, **kwargs):
        """
        Run handles some command to singularity (e.g., run or exec)
        """
        command = "%s %s singularity %s" % (self.path, self.environ, " ".join(args[0]))

        # If the user wants a shell, give to them!
        if "shell" in args[0]:
            self.ssh.shell(command, interactive=True)
        else:
            res = self.ssh.execute(command)
            self.ssh.print_output(res)


def post_commands(ssh, app, socket):
    time.sleep(10)
    ssh.tunnel_login_node(socket=socket, app=app)
    if app.post_command:
        logger.info("Found post command %s" % app.post_command)
        post = app.post_command.replace("$socket_dir", os.path.dirname(socket))
        ssh.execute(shlex.split(post), stream=True)
    time.sleep(30)
    ssh.tunnel_login_node(socket=socket, app=app)
