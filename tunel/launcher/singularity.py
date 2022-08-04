__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from tunel.logger import logger
import tunel.utils as utils

import threading
import time
import os

from tunel.launcher.base import Launcher


class Singularity(Launcher):
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
        logger.c.print()
        logger.c.print("== INSTRUCTIONS WILL BE PRINTED with a delay ==")
        command = "%s %s %s %s" % (
            self.path,
            self.environ,
            self.ssh.settings.shell,
            remote_script,
        )
        self.print_tunnel_instructions(app, render["socket"])
        self.ssh.execute(command, stream=True)

    def print_tunnel_instructions(self, app, socket):
        """
        Start a separate thread to print connection details.
        """
        thread = threading.Thread(
            target=print_tunnel_instructions,
            name="Logger",
            args=[self.ssh, app, socket],
        )
        thread.start()


def print_tunnel_instructions(ssh, app, socket):
    time.sleep(10)
    ssh.tunnel_login_node(socket=socket, app=app)
    time.sleep(30)
    ssh.tunnel_login_node(socket=socket, app=app)
