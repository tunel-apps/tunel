#!/bin/bash

JOB_NAME="{{ jobname }}"
SOCKET_DIR="{{ scriptdir }}"
mkdir -p ${SOCKET_DIR}

# Use TMP as a cache for now
export SINGULARITY_CACHEDIR=/tmp

# Working Directory
NOTEBOOK_DIR=$1
cd $NOTEBOOK_DIR

echo "Job is ${JOB_NAME}"
echo "Socket directory is ${SOCKET_DIR}"
echo "Notebook working directory is ${NOTEBOOK_DIR}"
cd ${NOTEBOOK_DIR}

# Create .local folder for default modules, if doesn't exist
if [ ! -d "${HOME}/.local" ]; then
    echo "Creating local python modules folder to map at ${HOME}/.local";
    mkdir -p "${HOME}/.local";
fi

# Remove socket if exists
SOCKET="${SOCKET_DIR}/{{ jobslug }}.sock"
if [[ -f "${SOCKET}" ]]; then
    echo "Removing existing socket ${SOCKET}"
    rm ${SOCKET}
fi

# Load modules requested by user
{% for module in modules %}module load {{ module }} || printf "Could not load {{ module }}\n"
{% endfor %}

# Add variables to PATH
{% for path in paths %}export PATH={{ path }}:${PATH}
{% endfor %}

# Just pull to tmp for now so cleaned up
CONTAINER="${SINGULARITY_CACHEDIR}/datascience-notebook.sif"

# First effort
if command -v singularity &> /dev/null
then
    printf "singularity pull docker://jupyter/datascience-notebook\n"
    singularity pull ${CONTAINER} "docker://jupyter/datascience-notebook"
    printf "singularity exec --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local ${CONTAINER} jupyter notebook --no-browser --sock ${SOCKET}\n"
    singularity exec {% if args.jupyterlab %}--env JUPYTER_ENABLE_LAB=yes{% endif %} --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local --bind ${HOME}/.jupyter:/home/jovyan/.jupyter "${CONTAINER}" jupyter notebook --no-browser --sock ${SOCKET}
else
    printf "Singularity is not available.\n"
fi
