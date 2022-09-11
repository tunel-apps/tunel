from tunel.logger import logger

from .base import Launcher
from .docker import Docker
from .htcondor import HTCondor
from .podman import Podman
from .singularity import Singularity
from .slurm import Slurm


def get_launcher(app, launcher=None):
    """
    Get a launcher for a loaded app
    """
    # No go if the launcher is defined and not tested for the app
    if launcher and launcher not in app.launchers:
        logger.exit(f"Launcher {launcher} has not been tested for app {app.name}")

    # Otherwise, should be ok!
    if launcher:
        app.launcher = launcher

    if app.launcher in ["htcondor", "condor"]:
        return HTCondor
    if app.launcher == "slurm":
        return Slurm
    if app.launcher == "podman":
        return Podman
    if app.launcher == "docker":
        return Docker
    elif app.launcher == "singularity":
        return Singularity
    return Launcher
