__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


import os

from jinja2 import Environment, FileSystemLoader

here = os.path.dirname(os.path.abspath(__file__))

# Allow includes from this directory OR providing strings
shared_templates_dir = os.path.join(here, "templates")


class Template:
    """
    Supporting functions for loading any kind of apps template
    """

    def get(self, template_name, template_dir=None):
        """
        Get a template from templates
        """
        template_file = os.path.join(here, "templates", template_name)
        if template_dir and not os.path.exists(template_file):
            template_file = os.path.join(template_dir, template_name)
        if not os.path.exists(template_file):
            template_file = os.path.abspath(template_name)
        return template_file

    def load(self, template_name, template_dir=None):
        """
        Load the default module template.
        """
        template_file = self.get(template_name, template_dir)
        with open(template_file, "r") as temp:
            # If we are given an app template directory, respect it and add to loader
            if template_dir:
                env = Environment(
                    loader=FileSystemLoader([shared_templates_dir, template_dir])
                )
            else:
                env = Environment(loader=FileSystemLoader(shared_templates_dir))
            template = env.from_string(temp.read())
        return template
