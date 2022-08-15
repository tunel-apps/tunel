__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import shlex
import threading
import time

import tunel.utils as utils
from tunel.launcher.base import Launcher
from tunel.logger import logger


class Docker(Launcher):
    name = "docker"

    def run(self, *args, **kwargs):
        """
        Run handles some command to docker (this can be expanded in functionality)
        """
        if self.path:
            command = "docker run -d --rm -i %s PATH=%s %s" % (
                self.env_command,
                self.path,
                " ".join(args[0]),
            )
        else:
            command = "docker run -d --rm -i %s %s" % (
                self.env_command,
                " ".join(args[0]),
            )

        res = self.ssh.execute(command)
        self.ssh.print_output(res)

    @property
    def env_command(self):
        """
        Transform a listing of key=value into docker --env flags
        """
        envars = self.environ.split(" ") if self.environ else ""
        if envars:
            envars = ["--env %s" for e in envars]
            envars = " ".join(envars)
        return envars

    def run_app(self, app):
        """
        Run a docker container directly on your remote resource.
        """
        # Make sure we set the username to the ssh
        self.username

        # Add any paths from the config
        paths = self.settings.get("paths", [])

        # Prepare dictionary with content to render into recipes
        render = self.prepare_render(app, paths)
        render["docker"] = self.name

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

    def stop_app(self, app):
        """
        Wrapper to stop a single app.
        """
        return self.stop([app.name])

    def stop(self, names):
        """
        Stop one or more named jobs
        """
        for name in names:
            name = name.replace("/", "-")
            logger.purple("Killing %s docker container on %s" % (name, self.ssh.server))
            self.ssh.execute_or_fail("docker stop %s" % name)
            self.ssh.execute_or_fail("docker rm %s || echo Already removed." % name)

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
