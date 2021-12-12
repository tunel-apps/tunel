__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from tunel.logger import logger
from tunel.launcher.base import Launcher
import tunel.utils as utils
import tunel.ssh
import os

here = os.path.dirname(os.path.abspath(__file__))


class Slurm(Launcher):
    """
    A slurm launcher interacts with slurm
    """

    def __init__(self, server, **kwargs):
        super().__init__(server, **kwargs)
        self._inventory = {}

    @property
    def modules_file(self):
        return os.path.join(self.assets_dir, "modules.txt")

    @property
    def nodes_file(self):
        return os.path.join(self.assets_dir, "sinfo.txt")

    def update_inventory(self):
        if self._inventory:
            return
        self._update_inventory_modules()
        self._update_inventory_nodes()

    def _update_inventory_nodes(self):
        """
        Try to derive attributes for nodes
        """
        if not os.path.exists(self.nodes_file):
            res = self.ssh.execute("scontrol show config")
            tunel.utils.write_file(self.nodes_file, res["message"])
        if os.path.exists(self.nodes_file) and "nodes" not in self._inventory:
            self._inventory["nodes"] = tunel.utils.read_config_file(self.nodes_file)

    def _update_inventory_modules(self):
        """
        Try to derive list of installed modules on cluster.
        This has been tested for LMOD
        """
        # if we don't have modules, write there
        if not os.path.exists(self.modules_file):
            res = self.scp_and_run("list_modules.sh")
            if res["return_code"] == 0:
                res = [x for x in res["message"].split("\n") if "RESULT:" in x]

                # This is the output file with list of modules
                if res:
                    res = res[0].split(":")[-1]

                    # scp get is copying FROM the server to assets here
                    self.scp_get(res, self.modules_file)

        # When we get here, only will exist if command was successful
        if os.path.exists(self.modules_file) and "modules" not in self._inventory:
            self._inventory["modules"] = tunel.utils.read_lines(self.modules_file)

    def run_app(self, app):
        """
        Given an app designated for slurm, run it!
        """
        self.update_inventory()

        # Prepare dictionary with content to render into recipes
        render = {}

        # TODO need to test with something that needs a module
        if app.needs:
            render["modules"] = self.get_modules(app.needs.get("modules"))
            render["args"] = self.get_args(app.needs.get("args"))

        # TODO render script with jinja2

        # Copy over to server
        script = app.get_script()
        remote_script = os.path.join(self.remote_assets_dir, app.name, app.script)
        self.ssh.scp_to(script, remote_script)

        # The script is required
        command = ["sbatch", remote_script] + render.get("args", [])

        # Launch with command
        res = self.ssh.execute(command)

    def run(self, *args, **kwargs):
        """
        Run a command for slurm, typically sbatch (and eventually with supporting args)
        """
        self.update_inventory()

        # If no command, get interactive node
        cmd = args[0]
        if not cmd:
            logger.info("No command supplied, will init interactive session!")
            self.ssh.shell("srun --pty bash", interactive=True)

        # TODO develop workflow for script
        else:
            res = self.ssh.execute("sbatch %s" % " ".join(cmd))
            self.ssh.print_output(res)
