__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"


from tunel.logger import logger
from tunel.ssh import Tunnel


def list_apps(args, parser, extra, subparser):
    """
    List installed apps
    """
    import tunel.apps

    apps = tunel.apps.list_apps()
    if not apps:
        logger.exit("There aren't any applications found in your apps paths.", 0)

    print("%-20s %s" % ("Name", "Launcher"))
    for name, app in apps.items():
        logger.info("%-20s %s" % (name, app.launcher))
