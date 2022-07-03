__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"


from tunel.ssh import Tunnel


def main(args, parser, extra, subparser):
    tunel = Tunnel(args.server)
    output = tunel.execute_or_fail(extra)
    for line in output.split("\n"):
        if not line:
            continue
        print(" " + line)
