__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os
import shlex
import threading
import time

import tunel.utils
from tunel.launcher.base import Launcher
from tunel.logger import logger

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

    def _prepare_render(self, app, paths):
        """
        Given an app, prepare default variables (and custom args) to render
        """
        render = {}
        # TODO needs should not be hard coded for slurm
        if app.needs:
            render["modules"] = self.get_modules(app.needs.get("modules"))
        return render

    def run_app(self, app):
        """
        Given an app designated for slurm, run it!
        """
        self.update_inventory()

        # Add any paths from the config
        paths = self.settings.get("paths", [])

        # Prepare dictionary with content to render into recipes
        render = self.prepare_render(app, paths)
        remote_script = render["script"]

        # Clean up previous sockets
        self.ssh.execute(["rm", "-rf", "%s/*.sock" % render["scriptdir"]])

        # Load the app template
        template = app.load_template()
        result = template.render(**render)

        # Write script to temporary file
        tmpfile = self.write_temporary_script(result)

        # Copy over to server
        self.ssh.scp_to(tmpfile, render["script"])
        os.remove(tmpfile)

        # Assemble the command
        if app.has_xserver:
            command = [
                "srun",
                "--job-name=%s" % app.job_name,
                "--pty",
                "/bin/bash",
                remote_script,
            ]
        else:
            command = [
                "sbatch",
                "--job-name=%s" % app.job_name,
                "--output=%s" % render["log_output"],
                "--error=%s" % render["log_error"],
                remote_script,
            ]

        # Launch with command
        if not self.previous_job_exists(app.job_name):
            self.run(
                command,
                app.job_name,
                logs_prefix=remote_script,
                app=app,
                socket=render["socket"],
            )

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
            logger.purple("Killing %s slurm job on %s" % (name, self.ssh.server))
            self.ssh.execute_or_fail(
                "squeue --name %s --user %s" % (name, self.username)
                + " -o '%A' -h | xargs --no-run-if-empty /usr/bin/scancel"
            )
            logger.purple("Killing listeners on %s" % self.ssh.server)
            self.ssh.execute_or_fail(
                "lsof -i :%s -t | xargs --no-run-if-empty kill" % self.ssh.remote_port
            )

    def previous_job_exists(self, name):
        """
        Check to see if a previous job was submit/exists.
        """
        logger.purple("Checking for previous run of %s" % name)
        previous = self.ssh.execute_or_fail(
            "squeue --name %s --user %s" % (name, self.username) + " -o %R -h"
        )
        if previous == "":
            logger.purple("No existing %s jobs found, continuing." % name)
        else:
            logger.error("Found existing job for %s!" % name)
            logger.exit(
                "Please run 'tunel stop-slurm %s %s' before proceeding."
                % (self.ssh.server, name)
            )

    def get_machine(self, name, max_attempts=None):
        """
        Given the name of a job, wait for the job to start and return the machine
        """
        max_attempts = max_attempts or self.settings.get("max_attempts")
        timeout = 2
        attempt = 1
        machine = ""
        allocated = False

        logger.purple("Waiting for job to start, using exponential backoff")

        # Continue waiting until machine is allocated
        while not allocated:
            with logger.c.status("Waiting...", spinner=self.ssh.settings.tunel_spinner):
                machine = self.ssh.execute_or_fail(
                    "squeue --name %s --user %s" % (name, self.username) + " -o %N -h"
                )
                if machine != "":
                    logger.purple(
                        "Attempt %s: resources allocated to %s!" % (attempt, machine)
                    )
                    allocated = True
                    break

                logger.purple(
                    "Attempt %s: not ready yet... retrying in %s..."
                    % (attempt, timeout)
                )
                time.sleep(timeout)
                attempt += 1
                if max_attempts and attempt >= max_attempts:
                    logger.exit(
                        f"Max attempts {max_attempts} reached, stopping trying."
                    )
                timeout = timeout * 2

        return machine

    def show_logs_instruction(self, logs_prefix):
        """
        print to the screen how to see currently running logs
        """
        logger.purple("View logs in separate terminal")
        logger.info("ssh %s cat %s.out" % (self.ssh.server, logs_prefix))
        logger.info("ssh %s cat %s.err" % (self.ssh.server, logs_prefix))
        print()

    def print_updated_logs(self, logs_prefix, app, socket):
        """
        Start a separate thread that regularly checks and prints logs (when there is an updated line)
        """
        logs_thread = threading.Thread(
            target=post_commands,
            name="Logger",
            args=[self.ssh, app, logs_prefix, socket],
        )
        logs_thread.start()

    def run(self, cmd, job_name=None, logs_prefix=None, app=None, socket=None):
        """
        Run a command for slurm, typically sbatch (and eventually with supporting args)
        """
        self.update_inventory()

        # Generate a name for the job, if not supplied
        if not job_name:
            job_name = tunel.utils.namer.generate()

        # If no command, get interactive node
        if not cmd:
            logger.info("No command supplied, will init interactive session!")
            self.ssh.shell("srun --pty bash", interactive=True)

        else:
            res = self.ssh.execute(" ".join(cmd), xserver=app.has_xserver)
            self.ssh.print_output(res)

            # A successful submission should:
            if res["return_code"] == 0 and not app.has_xserver:

                # 1. Show the user how to quickly get logs (if logs_prefix provided)
                if logs_prefix:
                    self.show_logs_instruction(logs_prefix)

                machine = self.get_machine(job_name)
                logger.info("%s is running on %s!" % (job_name, machine))

                # An xserver launches the app directly
                time.sleep(10)
                self.print_session_instructions(job_name)

                # Create another process to check logs?
                if logs_prefix:
                    self.print_updated_logs(logs_prefix, app, socket=socket)

                self.ssh.tunnel(machine, socket=socket, app=app)

    def print_session_instructions(self, job_name):
        """
        Print extra sessions with forward instructions.
        """
        # Setup port forwarding
        logger.c.print("== Connecting to %s ==" % job_name)
        logger.c.print("== Instructions ==")
        logger.c.print(
            "1. Password, output, and error will print to this - [bold]make sure application is ready before interaction."
        )
        logger.c.print(
            "3. To end session: tunel stop-slurm %s %s" % (self.ssh.server, job_name)
        )


def post_commands(ssh, app, logs_prefix, socket):
    """
    Post commands to show logs and any commands->post defined by the app
    """
    output_command = "ssh %s tail -3 %s.out" % (ssh.server, logs_prefix)
    error_command = "ssh %s tail -3 %s.err" % (ssh.server, logs_prefix)

    last_out = ""
    last_err = ""
    post_command = False
    while True:
        time.sleep(5)
        new_out = ssh.execute_or_fail(output_command, quiet=True)
        new_err = ssh.execute_or_fail(error_command, quiet=True)
        panels = {}

        # Show a post command (once), if defined
        if not post_command and app.post_command:
            logger.info("Found post command %s" % app.post_command)
            post = app.post_command.replace("$socket_dir", os.path.dirname(socket))
            ssh.execute(shlex.split(post), stream=True)
            post_command = True

        if new_out and new_out != last_out:
            panels["cyan"] = output_command + "\n" + new_out
            last_out = new_out
        if new_err and new_err != last_err:
            panels["magenta"] = error_command + "\n" + new_err
            last_err = new_err
        if panels:
            logger.panel_group(panels)
