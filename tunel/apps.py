__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from .settings import Settings
import tunel.defaults as defaults

from tunel.logger import logger
from tunel.template import Template
import tunel.utils as utils
import tunel.schemas
import tunel.template
import jsonschema
from datetime import datetime
import os
import sys


class App:
    def __init__(self, app_config, app_dir, validate=True):
        self.args = {}
        self.app_config = app_config
        self.app_root = app_dir
        self.load(validate)

    def __str__(self):
        return "[%s:%s]" % (self.launcher, self.name)

    def __repr__(self):
        return self.__str__()

    @property
    def app_dir(self):
        return os.path.dirname(self.app_config)

    @property
    def name(self):
        return os.path.dirname(self.relative_path)

    @property
    def job_name(self):
        return self.name.replace(os.sep, "-")

    @property
    def relative_path(self):
        return self.app_config.replace(self.app_root, "").strip("/")

    @property
    def relative_dir(self):
        return os.path.dirname(self.relative_path)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_script(self):
        return os.path.join(self.app_dir, self.script)

    def __getattr__(self, key):
        """
        A direct get of an attribute, but default to None if doesn't exist
        """
        return self.get(key)

    def docgen(self, out=None, outdir=None):
        """
        Render documentation for an app.
        """
        if outdir and not os.path.exists(outdir):
            logger.exit(f"{outdir} does not exist.")
        if outdir and os.path.exists(outdir):
            out = os.path.join(outdir, "%s.md" % self.job_name)
            out = open(out, "w")
        out = out or sys.stdout
        template = tunel.template.Template().load("docs.md")

        github_url = "%s/blob/main/tunel/apps/%s" % (
            defaults.github_url,
            self.relative_path,
        )
        script_url = "%s/blob/main/tunel/apps/%s/%s" % (
            defaults.github_url,
            self.relative_dir,
            self.script,
        )
        script = utils.read_file(self.get_script())

        # Currently one doc is rendered for all containers
        result = template.render(
            app=self,
            script="{% raw %}" + script + "{% endraw %}",
            script_url=script_url,
            github_url=github_url,
            creation_date=datetime.now(),
        )
        out.write(result)
        out.close()
        return result

    def add_args(self, extra):
        """
        Extra is a list of args, in either format:

        --name=value
        --flag

        They must start with -- to be considered.
        """
        args = {x["name"]: x.get("split") for x in self.config.get("args", {})}
        argkeys = ", ".join(list(args.keys()))
        for extra in extra:
            if not extra.startswith("--"):
                continue
            arg = extra.lstrip("--").split("=")
            if arg not in args:
                logger.warning(
                    f"{arg} is not a recognized argument, choices are {argkeys}"
                )
            if len(arg) == 1:
                self.args[arg[0]] = True
            elif len(arg) == 2:
                value = arg[1]
                splitby = args.get(arg[0])
                if splitby:
                    value = value.split(splitby)
                self.args[arg[0]] = value
            else:
                logger.warning(f"Unexpected argument: {extra}, skipping.")

    def load_template(self):
        """
        Given an app, load the template script for it.
        """
        template = Template()
        return template.load(self.get_script())

    def validate(self):
        """
        Validate the loaded settings with jsonschema
        """
        jsonschema.validate(self.config, schema=tunel.schemas.app_schema)

    def load(self, validate=True):
        self.config = utils.read_yaml(self.app_config)
        if validate:
            self.validate()


def get_app(app, extra=None):
    """
    Given an app name, get the loaded app for it
    """
    apps = list_apps()
    if app not in apps:
        logger.exit("Cannot find app %s\nChoices are:\n%s" % (app, "\n  ".join(apps)))
    app = apps[app]
    app.add_args(extra)
    return app


def list_apps(settings_file=None, validate=False):
    """
    Given the user settings,
    """
    settings_file = settings_file or defaults.default_settings_file
    settings = Settings(settings_file)
    apps = {}

    # parse through in reverse so top names take priority
    for app_dir in reversed(settings.apps_dirs):
        if not os.path.exists(app_dir):
            logger.warning("%s does not exist." % app_dir)
            continue

        # Look for apps that validate
        for filename in utils.recursive_find(app_dir, "app.yaml"):
            try:
                app = App(filename, app_dir)
            except Exception as e:
                if validate:
                    logger.exit("%s is not valid: %s" % (filename, e))
                else:
                    logger.error("%s is not valid" % (filename))
                    continue
            apps[app.name] = app

    return apps
