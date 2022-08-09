# This is an example of talking to an API deployed via socket to tunel.
# This uses the tunel-django app, which has a simple joke (JSON) api.
# Usage:
# python tunel_api.py /tmp/test/tunel-django.sock.api.sock

import json
import os
import sys
import tunel.api


def api_get(socket, path="/api/joke/"):
    """
    Get a joke from the tunel-django API.
    This is also provided from the command line in tunel:
    # tunel api-get --socket /tmp/test/tunel-django.sock.api.sock /api/joke/
    """
    api = tunel.api.ApiConnection(socket)
    res = api.get(path)
    print(json.dumps(res.json(), indent=4))
    # print(res.text)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit("Please provide the path to a tunel socket.")
    api_get(sys.argv[1])
