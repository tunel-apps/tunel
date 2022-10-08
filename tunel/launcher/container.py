__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import shlex
import threading
import time

import tunel.utils as utils
from tunel.logger import logger

from .base import Launcher


class ContainerLauncher(Launcher):
    """
    A container launcher has shared functions for launching a head node container.
    """

    name = "container"

    def run_app(self, app):
        """
        A Singularity app means running a container directly with some arguments, etc.
        """
        # Make sure we set the username to the ssh
        self.username

        # Add any paths from the config
        paths = self.settings.get("paths", [])

        # Prepare dictionary with content to render into recipes
        render = self.prepare_render(app, paths)
        render[self.name] = self.name

        # Clean up previous sockets
        self.ssh.execute(["rm", "-rf", "%s/*.sock" % render["scriptdir"]])

        # Load the app template
        template = app.load_template()
        result = template.render(**render)

        # Write script to temporary file
        tmpfile = utils.get_tmpfile()
        utils.write_file(tmpfile, result)

        # Copy over to server
        remote_script = os.path.join(self.remote_assets_dir, app.name, app.script)
        self.ssh.scp_to(tmpfile, remote_script)

        # Instead of a Singularity command, we run the script
        command = "%s %s %s %s" % (
            self.path,
            self.environ,
            self.ssh.settings.shell,
            remote_script,
        )

        # An xserver launches the app directly
        if not app.has_xserver:
            logger.c.print()
            logger.c.print("== INSTRUCTIONS WILL BE PRINTED with a delay ==")
            self.print_tunnel_instructions(app, render["socket"])
        self.ssh.execute(command, stream=True, xserver=app.has_xserver)

    def print_tunnel_instructions(self, app, socket):
        """
        Start a separate thread to print connection details.
        """
        thread = threading.Thread(
            target=post_commands,
            name="Logger",
            args=[self.ssh, app, socket],
        )
        thread.start()


def post_commands(ssh, app, socket):
    time.sleep(10)
    ssh.tunnel_login_node(socket=socket, app=app)
    if app.post_command:
        logger.info("Found post command %s" % app.post_command)
        post = app.post_command.replace("$socket_dir", os.path.dirname(socket))
        ssh.execute(shlex.split(post), stream=True)
    time.sleep(30)
    ssh.tunnel_login_node(socket=socket, app=app)
