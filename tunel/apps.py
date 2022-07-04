__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from .settings import Settings
import tunel.defaults as defaults

from tunel.logger import logger
from tunel.template import Template
import tunel.utils as utils
import tunel.schemas
import jsonschema
import os


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

    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_script(self):
        return os.path.join(self.app_dir, self.script)

    def __getattr__(self, key):
        """
        A direct get of an attribute, but default to None if doesn't exist
        """
        return self.get(key)

    def add_args(self, extra):
        """
        Extra is a list of args, in either format:

        --name=value
        --flag

        They must start with -- to be considered.
        """
        for extra in extra:
            if not extra.startswith("--"):
                continue
            arg = extra.lstrip("--").split("=")
            if len(arg) == 1:
                self.args[arg[0]] = True
            elif len(arg) == 2:
                self.args[arg[0]] = arg[1]
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
            except:
                if validate:
                    logger.exit("%s is not valid" % (filename))
                else:
                    logger.error("%s is not valid" % (filename))
                    continue
            apps[app.name] = app

    return apps
