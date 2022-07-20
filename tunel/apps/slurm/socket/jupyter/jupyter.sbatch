#!/bin/bash

JOB_NAME="{{ jobname }}"
SOCKET_DIR="{{ scriptdir }}"
mkdir -p ${SOCKET_DIR}

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

printf "jupyter notebook --no-browser --sock ${SOCKET}\n"
{% if args.jupyterlab %}export JUPYTER_ENABLE_LAB=yes{% endif %}
jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --sock ${SOCKET}
