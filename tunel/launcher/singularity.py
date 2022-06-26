__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from tunel.logger import logger
import tunel.utils as utils
import tunel.ssh
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
