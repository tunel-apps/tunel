__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import tunel.apps
from tunel.logger import logger
from rich.table import Table


def list_apps(args, parser, extra, subparser):
    """
    List installed apps
    """
    apps = tunel.apps.list_apps(validate=args.validate)
    if not apps:
        logger.exit("There aren't any applications found in your apps paths.", 0)

    table = Table(title="Tunel Apps")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Launcher", justify="right", style="green")

    for i, app in enumerate(apps.items()):
        name, app = app
        table.add_row(str(i), name, app.launcher)

    logger.c.print(table, justify="center")
