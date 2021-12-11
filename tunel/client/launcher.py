__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


from tunel.logger import logger
import tunel.launcher


def run_singularity(args, parser, extra, subparser):

    launcher = tunel.launcher.Singularity(
        args.server, remote_port=args.port, local_port=args.local_port
    )
    launcher.run(extra)


def run_slurm(args, parser, extra, subparser):

    launcher = tunel.launcher.Slurm(
        args.server, remote_port=args.port, local_port=args.local_port
    )
    launcher.run(extra)
