#!/bin/bash

# NOTE THIS PORT METHOD IS NOT TESTED YET

# Sets $PORT envar from args.port then port
{% include "bash/network/set-port.sh" %}

# Working Directory
{% include "bash/set-workdir.sh" %}
cd $WORKDIR

echo "Port is ${PORT}"
echo "Notebook working directory is ${WORKDIR}"

# Create .local folder for default modules, if doesn't exist
{% include "bash/python/create-local.sh" %}

# Load modules requested by user
{% for module in args.modules %}module load {{ module }} || printf "Could not load {{ module }}\n"
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
    printf "singularity exec --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local docker://jupyter/datascience-notebook jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --port=$PORT --ip 0.0.0.0\n"
    singularity exec --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local "docker://jupyter/datascience-notebook" jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --port=$PORT --ip 0.0.0.0
else
    printf "Singularity not available, trying native jupyter.\n"
    printf "jupyter notebook --no-browser --port=$PORT\n"
    jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --port=$PORT
fi
