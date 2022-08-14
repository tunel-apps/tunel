#!/bin/bash

JOB_NAME="{{ jobname }}"
SOCKET_DIR="{{ scriptdir }}"
mkdir -p ${SOCKET_DIR}

# Include Singularity cachedir if not set
{% include "bash/singularity/set-cache-tmp.sh" %}

# Source ~/bash_profile or ~/.profile
{% include "bash/source-profile.sh" %}

# Set WORKDIR, first to args.workdir, then settings.yml workdir, then $HOME
{% include "bash/set-workdir.sh" %}
cd $WORKDIR

echo "Job is ${JOB_NAME}"
echo "Socket directory is ${SOCKET_DIR}"
echo "Notebook working directory is ${WORKDIR}"

# Create .local folder for default modules, if doesn't exist
{% include "bash/python/create-local.sh" %}

# Remove socket if exists
{% include "bash/socket/set-socket.sh" %}

# Load modules requested by user
{% for module in args.modules %}module load {{ module }} || printf "Could not load {{ module }}\n"
{% endfor %}

# Add variables to PATH
{% for path in paths %}export PATH={{ path }}:${PATH}
{% endfor %}

# Just pull to tmp for now so cleaned up
SIF="${SINGULARITY_CACHEDIR}/jupyter-notebook.sif"
CONTAINER="{% if args.container %}{{ args.container }}{% else %}docker://jupyter/datascience-notebook{% endif %}"

# First effort
if command -v singularity &> /dev/null
then
    printf "singularity pull ${CONTAINER}\n"

    # Only pull the container if we do not have it yet
    if [[ ! -f "${SIF}" ]]; then
        singularity pull ${SIF} ${CONTAINER}
    fi

    # In case they don't exist yet
    mkdir -p $HOME/.jupyter

    printf "singularity exec {% if args.jupyterlab %}--env JUPYTER_ENABLE_LAB=yes{% endif %} --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local ${CONTAINER} jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --sock ${SOCKET}\n"
    singularity exec {% if args.jupyterlab %}--env JUPYTER_ENABLE_LAB=yes{% endif %} --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local --bind ${HOME}/.jupyter:/home/jovyan/.jupyter "${SIF}" jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --sock ${SOCKET}
else
    printf "Singularity is not available.\n"
fi
