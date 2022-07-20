#!/bin/bash

JOB_NAME="{{ jobname }}"
SOCKET_DIR="{{ scriptdir }}"
mkdir -p ${SOCKET_DIR}

# Include Singularity cachedir if not set
{% include "bash/singularity/set-cache-tmp.sh" %}

# Working Directory
NOTEBOOK_DIR={% if args.workdir %}{{ args.workdir }}{% else %}$HOME{% endif %}
cd $NOTEBOOK_DIR

echo "Job is ${JOB_NAME}"
echo "Socket directory is ${SOCKET_DIR}"
echo "Notebook working directory is ${NOTEBOOK_DIR}"

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
SIF="${SINGULARITY_CACHEDIR}/datascience-notebook.sif"
CONTAINER="{% if args.container %}{{ args.container }}{% else %}docker://jupyter/datascience-notebook{% endif %}"

# First effort
if command -v singularity &> /dev/null
then
    printf "singularity pull ${SIF} ${CONTAINER}\n"
    singularity pull ${SIF} ${CONTAINER}

    # In case doesn't exist yet
    mkdir -p $HOME/.jupyter

    printf "singularity exec --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local ${CONTAINER} jupyter notebook --no-browser --sock ${SOCKET}\n"
    singularity exec {% if args.jupyterlab %}--env JUPYTER_ENABLE_LAB=yes{% endif %} --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local --bind ${HOME}/.jupyter:/home/jovyan/.jupyter "${CONTAINER}" jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --sock ${SOCKET}
else
    printf "Singularity is not available.\n"
fi
