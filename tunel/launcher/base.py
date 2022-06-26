__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from tunel.logger import logger
import tunel.utils as utils
import tunel.ssh
import os

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

    def get_args(self, args):
        """
        Given a list of needed args, return values
        """
        # TODO this should be a dict of kwargs, and defaults should be
        # provided to render
        choices = []
        for arg in args:
            if arg == "port":
                choices.append(str(self.ssh.remote_port))
            elif arg == "workdir":
                choices.append(self.remote_work)
            else:
                logger.warning("%s is not a known argument type" % arg)
        return choices

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
        Get (or create) a local home
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
