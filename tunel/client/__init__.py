#!/usr/bin/env python

__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import argparse
import os
import sys

import tunel
from tunel.logger import setup_logger


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

    info = subparsers.add_parser(
        "info",
        description="Get information about a named app.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Tunel api-get means we issue a GET request to an endpoint
    api_get = subparsers.add_parser(
        "api-get",
        description="interact with the GET api of a tunel app.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    api_get.add_argument("--socket", help="path to tunel mapped socket")
    api_get.add_argument("path", help="path to GET (defaults to /)")

    for command in info, api_get:
        command.add_argument(
            "--json",
            help="provide result as json",
            default=False,
            action="store_true",
        )

    # Local shell with client loaded
    shell = subparsers.add_parser(
        "shell",
        description="shell into a remote connection",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Also support sh
    sh = subparsers.add_parser(
        "sh",
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
    run_docker = subparsers.add_parser(
        "run-docker",
        description="launch an interactive docker container.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    run_slurm = subparsers.add_parser(
        "run-slurm",
        description="launch a slurm job or session.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    run_condor = subparsers.add_parser(
        "run-condor",
        description="launch an htcondor job or session.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Stop a slurm running application
    stop_slurm = subparsers.add_parser(
        "stop-slurm",
        description="stop or kill a slurm job or session.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    stop_condor = subparsers.add_parser(
        "stop-condor",
        description="stop or kill an HTCondor job or session.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Apps
    run_app = subparsers.add_parser(
        "run-app",
        description="run a named application",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    stop_app = subparsers.add_parser(
        "stop-app",
        description="stop a named application",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    list_app = subparsers.add_parser(
        "list-apps",
        description="list apps found on the known settings paths",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    list_app.add_argument(
        "--validate",
        help="validate apps loading",
        default=False,
        action="store_true",
    )
    docgen = subparsers.add_parser(
        "docgen",
        description="generate docs (markdown) for apps",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    docgen.add_argument(
        "outdir",
        help="Output directory to write apps markdown",
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

    launchers = [
        run_docker,
        run_singularity,
        run_slurm,
        run_app,
        stop_app,
        stop_slurm,
        run_condor,
        stop_condor,
    ]

    # Run app can take a --launcher preference
    for command in run_app, stop_app:
        command.add_argument("--launcher", help="specify a non-default launcher to use")

    for command in [tunnel] + launchers:
        command.add_argument("--port", help="remote port to connect to.")
        command.add_argument("--local-port", help="local port to connect to.")

    for command in [
        sh,
        shell,
        execute,
        tunnel,
    ] + launchers:
        command.add_argument(
            "server",
            help="server identity to interact with (e.g., name in ~/.ssh/config)",
        )

    for command in [run_app, stop_app, info]:
        command.add_argument("app", help="The name of the application.")
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
    if args.command in ["shell", "sh"]:
        from .shell import main
    if args.command == "api-get":
        from .api import api_get as main
    if args.command == "docgen":
        from .apps import docgen as main
    if args.command == "exec":
        from .execute import main
    if args.command == "info":
        from .info import main
    if args.command == "tunnel":
        from .tunnel import main
    if args.command == "run-docker":
        from .launcher import run_docker as main
    if args.command == "run-singularity":
        from .launcher import run_singularity as main
    if args.command == "run-slurm":
        from .launcher import run_slurm as main
    if args.command == "run-condor":
        from .launcher import run_condor as main
    if args.command == "stop-slurm":
        from .launcher import stop_slurm as main
    if args.command == "stop-condor":
        from .launcher import stop_condor as main
    if args.command == "run-app":
        from .launcher import run_app as main
    if args.command == "stop-app":
        from .launcher import stop_app as main
    if args.command == "list-apps":
        from .apps import list_apps as main

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
