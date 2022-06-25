#!/bin/bash

JOB_NAME="{{ jobname }}"
SOCKET_DIR="{{ scriptdir }}"
mkdir -p ${SOCKET_DIR}

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

printf "jupyter notebook --no-browser --sock ${SOCKET}\n"
jupyter notebook --no-browser --sock ${SOCKET}
