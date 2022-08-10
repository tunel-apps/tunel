__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

# Get info for an app

import json

import tunel.apps


def main(args, parser, extra, subparser):
    app = tunel.apps.get_app(args.app, extra)
    if args.json:
        print(json.dumps(app.config, indent=4))
        return

    app.print_pretty()
