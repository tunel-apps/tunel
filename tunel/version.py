__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"

__version__ = "0.0.18"
AUTHOR = "Vanessa Sochat"
NAME = "tunel"
PACKAGE_URL = "https://github.com/tunel-apps/tunel"
KEYWORDS = "interface, ui, developer, HPC, containers"
DESCRIPTION = "Developer interfaces for HPC via tunneling"
LICENSE = "LICENSE"

################################################################################
# Global requirements

# Since we assume wanting Singularity and lmod, we require spython and Jinja2

INSTALL_REQUIRES = (
    ("jsonschema", {"min_version": None}),
    ("pyaml", {"min_version": None}),
    ("jinja2", {"min_version": None}),
    ("rich", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
