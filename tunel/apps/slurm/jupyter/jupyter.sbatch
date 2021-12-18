#!/bin/bash

PORT=$1
NOTEBOOK_DIR=$2
cd $NOTEBOOK_DIR

echo "Port is ${PORT}"
echo "Notebook working directory is ${NOTEBOOK_DIR}"
cd ${NOTEBOOK_DIR}

# Create .local folder for default modules, if doesn't exist
if [ ! -d "${HOME}/.local" ]; then
    echo "Creating local python modules folder to map at ${HOME}/.local";
    mkdir -p "${HOME}/.local";
fi

# Load modules requested by user
{% for module in modules %}module load {{ module }} || printf "Could not load {{ module }}\n"
{% endfor %}

# Add variables to PATH
{% for path in paths %}export PATH={{ path }}:${PATH}
{% endfor %}

module load singularity || printf "Singularity is not available as a module."

# First effort - 
if command -v singularity &> /dev/null
then
    printf "singularity pull docker://jupyter/datascience-notebook\n"
    singularity pull "docker://jupyter/datascience-notebook"
    printf "singularity pull docker://jupyter/datascience-notebook\n"
    printf "singularity exec --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local docker://jupyter/datascience-notebook jupyter notebook --no-browser --port=$PORT --ip 0.0.0.0\n"
    singularity exec --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local "docker://jupyter/datascience-notebook" jupyter notebook --no-browser --port=$PORT --ip 0.0.0.0
else
    printf "Singularity not available, trying native jupyter.\n"
    printf "jupyter notebook --no-browser --port=$PORT\n"
    jupyter notebook --no-browser --port=$PORT
fi
