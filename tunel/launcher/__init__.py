from .base import Launcher
from .slurm import Slurm
from .singularity import Singularity


def get_launcher(app):
    """
    Get a launcher for a loaded app
    """
    if app.launcher == "slurm":
        return Slurm
    elif app.launcher == "singularity":
        return Singularity
    return Launcher
