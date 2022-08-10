__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os

import tunel.ssh
import tunel.template
from tunel.launcher.base import Launcher
from tunel.logger import logger

here = os.path.dirname(os.path.abspath(__file__))


class HTCondor(Launcher):
    """
    An HTCondor interacts with condor
    """

    def run_app(self, app):
        """
        Given an app designated for htcondor, run it!
        """
        # Add any paths from the config
        paths = self.settings.get("paths", [])

        # Prepare dictionary with content to render into recipes
        render = self.prepare_render(app, paths)

        # Update memory if not in args
        if "memory" not in render["args"]:
            render["args"]["memory"] = self.settings["memory"]

        # Clean up previous sockets
        self.ssh.execute(["rm", "-rf", "%s/*.sock" % render["scriptdir"]])

        # Load the app template
        template = app.load_template()
        result = template.render(**render)

        # We also need to render the template for the submit
        template = tunel.template.Template()
        job_template = template.load("htcondor/template.submit")
        job_submit = job_template.render(**render)

        # Write the job script to the cluster
        tmpfile = self.write_temporary_script(result)
        self.ssh.scp_to(tmpfile, render["script"])
        os.remove(tmpfile)

        # And the submit script
        tmpfile = self.write_temporary_script(job_submit)
        submit_file = render["script"] + ".submit"
        self.ssh.scp_to(tmpfile, submit_file)
        os.remove(tmpfile)

        # Assemble the command
        command = ["condor_submit", submit_file, "-batch-name", app.job_name]

        # Launch with command
        if not self.previous_job_exists(app.job_name):
            self.run(command)

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
            logger.purple("Killing %s condor job on %s" % (name, self.ssh.server))
            job = self.get_job(name)
            if job:
                _, jobid = job.rsplit(" ", 1)
                self.ssh.execute_or_fail("condor_rm %s" % jobid)

    def get_job(self, name):
        """
        Get a job by name (the unparsed line)
        """
        lines = self.ssh.execute_or_fail("condor_q %s" % self.username)
        for line in lines.split("\n"):
            if line.startswith(self.username):
                owner, job_name, rest = line.split(" ", 2)
                if name == job_name:
                    return line

    def previous_job_exists(self, name):
        """
        Check to see if a previous job was submit/exists.
        """
        logger.purple("Checking for previous run of %s" % name)
        job = self.get_job(name)
        if job:
            logger.error("Found existing job for %s!" % name)
            logger.exit(
                "Please run 'tunel stop-condor %s %s' before proceeding."
                % (self.ssh.server, name)
            )
        logger.purple("No existing %s jobs found, continuing." % name)

    def run(self, cmd):
        """
        Run a command for htcondor
        """
        # If no command, get interactive node
        if not cmd:
            logger.info("No command supplied, will init interactive session!")
            self.ssh.shell("condor_submit -interactive", interactive=True)

        else:
            res = self.ssh.execute(" ".join(cmd))

            # A successful submission should:
            if res["return_code"] == 0:
                logger.c.print(res["message"])
