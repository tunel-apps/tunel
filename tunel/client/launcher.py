__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from tunel.logger import logger
import tunel.launcher
import tunel.apps

# Generic stop


def run_app(args, parser, extra, subparser):
    app = tunel.apps.get_app(args.app)
    launcher = tunel.launcher.get_launcher(app)(
        args.server, remote_port=args.port, local_port=args.local_port
    )
    launcher.run_app(app)


def stop_app(args, parser, extra, subparser):
    app = tunel.apps.get_app(args.app)
    launcher = tunel.launcher.get_launcher(app)(
        args.server, remote_port=args.port, local_port=args.local_port
    )
    launcher.stop_app(app)


# Specific to launcher


def run_singularity(args, parser, extra, subparser):

    launcher = tunel.launcher.Singularity(
        args.server, remote_port=args.port, local_port=args.local_port
    )
    launcher.run(extra)


def stop_slurm(args, parser, extra, subparser):
    launcher = tunel.launcher.Slurm(
        args.server, remote_port=args.port, local_port=args.local_port
    )
    launcher.stop(extra)


def run_slurm(args, parser, extra, subparser):

    launcher = tunel.launcher.Slurm(
        args.server, remote_port=args.port, local_port=args.local_port
    )
    launcher.run(extra)
