__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from tunel.logger import logger
from tunel.ssh import Tunnel


def main(args, parser, extra, subparser):

    tunel = Tunnel(args.server)
    output = tunel.execute(extra)

    # We will either have output or error
    if output["out"]:
        for line in output["out"]:
            print(line)
    if output["err"]:
        for line in output["err"]:
            logger.error(line)
