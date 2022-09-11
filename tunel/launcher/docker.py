__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from tunel.logger import logger

from .container import ContainerLauncher


class Docker(ContainerLauncher):
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
