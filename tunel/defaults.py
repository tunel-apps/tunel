__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import os

import tunel.utils as utils

install_dir = utils.get_installdir()

# Default apps directory
default_apps_dir = os.path.join(install_dir, "apps")

reps = {
    "$install_dir": install_dir,
    "$root_dir": os.path.dirname(install_dir),
    "$default_apps": default_apps_dir,
}

# The default settings file in the install root
default_settings_file = os.path.join(reps["$install_dir"], "settings.yml")

# The user settings file can be created to over-ride default
user_settings_file = os.path.join(os.path.expanduser("~/.tunel"), "settings.yml")

# variables in config we allow environment substitution
allowed_envars = ["ssh_config", "ssh_sockets", "tunel_home"]

# The GitHub repository with recipes (apps)
github_url = "https://github.com/tunel-apps/tunel"
