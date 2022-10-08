__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os

import tunel.ssh
import tunel.utils as utils
from tunel.logger import logger

here = os.path.dirname(os.path.abspath(__file__))


class Launcher:
    """
    A launcher is a base for executing commands.
    """

    def __init__(self, server, **kwargs):
        """
        The Launcher is not responsible for managing or closing the connection.
        """
        self.ssh = tunel.ssh.Tunnel(server, **kwargs)

        # A launcher can control assets locally or remotely
        self._remote_work = None
        self._remote_home = None
        self._remote_user = None
        self._home = None

        # Add launcher specific settings, if they exist.
        self.settings = {}
        if self.slug in self.ssh.settings.launchers:
            self.settings = self.ssh.settings.launchers[self.slug]

    @property
    def assets(self):
        return os.path.join(here, "scripts", self.slug)

    @property
    def slug(self):
        return str(self).lower()

    def __str__(self):
        return str(self.__class__.__name__)

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def run_app(self, *args, **kwargs):
        raise NotImplementedError

    def stop(self, *args, **kwargs):
        raise NotImplementedError

    def stop_app(self, *args, **kwargs):
        raise NotImplementedError

    def write_temporary_script(self, content):
        """
        Write a temporary script to file
        """
        tmpfile = utils.get_tmpfile()
        utils.write_file(tmpfile, content)
        return tmpfile

    def get_modules(self, needed_modules):
        """
        Given a list of needed modules, return for an app to load
        """
        if not needed_modules:
            return
        modules = self._inventory.get("modules")
        found_modules = []
        for needed_module in needed_modules:
            matches = [x for x in modules if needed_module in x]
            if matches:
                # Choose the last (likely latest version)
                found_modules += matches[-1]
        return found_modules

    def prepare_render(self, app, paths):
        """
        Given an app, prepare default variables (and custom args) to render
        """
        render = {"args": app.args}
        slug = app.name.replace(os.sep, "-").replace("/", "-")
        if app.needs:
            paths += app.needs.get("paths", [])
        render["jobslug"] = slug
        render["jobname"] = app.name
        render["port"] = self.ssh.remote_port
        render["scriptdir"] = os.path.join(self.remote_assets_dir, app.name)
        render["paths"] = paths
        render["socket"] = os.path.join(render["scriptdir"], "%s.sock" % slug)

        # Remote script, output and error files
        render["script"] = os.path.join(self.remote_assets_dir, app.name, app.script)
        render["script_basename"] = app.script
        render["log_output"] = render["script"] + ".out"
        render["log_error"] = render["script"] + ".err"
        render["log_file"] = render["script"] + ".log"

        # This is second priority to args.workdir
        if self.remote_work:
            render["workdir"] = self.remote_work
        if "workdir" in render["args"]:
            render["workdir"] = render["args"]

        # Does the subclass have customizations?
        if hasattr(self, "_prepare_render"):
            render.update(self._prepare_render(app, paths))
        return render

    @property
    def path(self):
        """
        Get additions to the path
        """
        paths = self.settings.get("paths", "")
        if paths:
            paths = "PATH=%s:$PATH" % (":".join(paths))
        return paths

    @property
    def environ(self):
        """
        Get envars
        """
        envars = self.settings.get("environment", "")
        if envars:
            envars = " ".join(envars)
        return envars

    @property
    def assets_dir(self):
        return os.path.join(self.home, "tunel", self.slug)

    @property
    def remote_assets_dir(self):
        return os.path.join(self.remote_home, "tunel", self.slug)

    @property
    def home(self):
        """
        Get (or create) a local home
        """
        if not self._home:
            self._home = self.ssh.settings.tunel_home
            if not os.path.exists(self.assets_dir):
                os.makedirs(self.assets_dir)
        return self._home

    @property
    def username(self):
        """
        Get the username
        """
        if not self._remote_user:
            self._remote_user = self.ssh.execute_or_fail("echo '$USER'")
            self.ssh.username = self._remote_user
        return self._remote_user

    @property
    def remote_home(self):
        """
        Get (or create) a remote home
        """
        if not self._remote_home:
            self._remote_home = self.ssh.execute_or_fail(
                "echo '%s'" % self.ssh.settings.tunel_remote_home, quiet=True
            )
            self.ssh.execute_or_fail("mkdir -p %s" % self.remote_assets_dir)
        return self._remote_home

    @property
    def remote_work(self):
        """
        Get a remote work (must exist)
        """
        if not self._remote_work:
            self._remote_work = self.ssh.execute_or_fail(
                "echo '%s'" % self.ssh.settings.tunel_remote_work
            )
        return self._remote_work

    @property
    def remote_sockets(self):
        """
        Get a remote sockets directory
        """
        if self.ssh.settings.tunel_remote_sockets:
            return self.ssh.settings.tunel_remote_sockets
        return os.path.join(self.remote_home, ".tunel", "sockets")

    def scp_get(self, src, dest):
        """
        Copy an asset FROM the server to local assets
        """
        dirname = os.path.dirname(dest)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return self.ssh.scp_from(src, dest)

    def scp_and_run(self, script):
        """
        Given a local script, copy to cluster, run, and return the result
        """
        # Remote modules file we will read
        remote_script = os.path.join(self.remote_assets_dir, script)

        # Local script to generate it (doesn't work interactivelt)
        local_script = os.path.join(self.assets, script)

        # Copy to the remote
        self.ssh.scp_to(local_script, remote_script)

        return self.ssh.execute(
            "chmod u+x %s; /bin/bash -l %s" % (remote_script, remote_script)
        )


class ContainerLauncher(Launcher):
    """
    A container launcher has shared functions for launching a head node container.
    """

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
