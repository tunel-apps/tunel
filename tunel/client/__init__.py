#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

import tunel
from tunel.logger import setup_logger
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(
        description="Tunel for ssh interface tunnels",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--settings-file",
        dest="settings_file",
        help="custom path to settings file.",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )

    description = "actions"
    subparsers = parser.add_subparsers(
        help="actions",
        title="actions",
        description=description,
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", description="show software version")

    # Local shell with client loaded
    shell = subparsers.add_parser(
        "shell",
        description="shell into a remote connection",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Run commands will issue launcher specific commands
    # tunel run-singularity <server> <container>
    run_singularity = subparsers.add_parser(
        "run-singularity",
        description="launch a singularity container.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Issue a command to a server
    execute = subparsers.add_parser(
        "exec",
        description="execute a command to a remote connection.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Open up a tunel (from local machine) to remote port
    tunnel = subparsers.add_parser(
        "tunnel",
        description="open up a tunnel to a remote port",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    tunnel.add_argument(
        "--isolated-nodes",
        help="if on a cluster, nodes are isolated",
        default=False,
        action="store_true",
    )

    for command in [tunnel, run_singularity]:
        command.add_argument("--port", help="remote port to connect to.")
        command.add_argument("--local-port", help="local port to connect to.")

    for command in [shell, execute, tunnel, run_singularity]:
        command.add_argument(
            "server",
            help="server identity to interact with (e.g., name in ~/.ssh/config)",
        )
    return parser


def run_tunel():

    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """

        version = tunel.__version__

        print("\nTunel v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    # TODO this could eventually run a UI
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(tunel.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    # Does the user want a shell?
    if args.command == "shell":
        from .shell import main
    if args.command == "exec":
        from .execute import main
    if args.command == "tunnel":
        from .tunnel import main
    if args.command == "run-singularity":
        from .launcher import run_singularity as main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args, parser=parser, extra=extra, subparser=helper)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)


if __name__ == "__main__":
    run_tunel()
