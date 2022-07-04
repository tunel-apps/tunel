from .base import Launcher
from .htcondor import HTCondor
from .slurm import Slurm
from .singularity import Singularity


def get_launcher(app):
    """
    Get a launcher for a loaded app
    """
    if app.launcher in ["htcondor", "condor"]:
        return HTCondor
    if app.launcher == "slurm":
        return Slurm
    elif app.launcher == "singularity":
        return Singularity
    return Launcher
