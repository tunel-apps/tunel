__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import json
import os
import tunel.api


def api_get(args, parser, extra, subparser):
    if not os.path.exists(args.socket):
        sys.exit("Socket for tunel %s does not exist." % args.socket)
    api = tunel.api.ApiConnection(args.socket)
    res = api.get(args.path)
    if args.json:
        print(json.dumps(res.json(), indent=4))
    else:
        print(res.text)
