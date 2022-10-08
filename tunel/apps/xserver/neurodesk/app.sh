#!/bin/bash

JOB_NAME="{{ jobname }}"
SCRIPT_DIR="{{ scriptdir }}"
mkdir -p ${SCRIPT_DIR}

# Sets $PORT envar from args.port then port
{% include "bash/network/set-port.sh" %}

# Include Singularity cachedir if not set
{% include "bash/singularity/set-cache-tmp.sh" %}

# Source ~/bash_profile or ~/.profile
{% include "bash/source-profile.sh" %}

# Working Directory
{% include "bash/set-workdir.sh" %}
cd $WORKDIR

echo "Job is ${JOB_NAME}"
echo "Port is ${PORT}"
echo "Working directory is ${WORKDIR}"
echo "Script directory is ${SCRIPT_DIR}"

# Create .local folder for default modules, if doesn't exist
{% include "bash/python/create-local.sh" %}

# username and password for django to create
{% include "bash/set-user-pass.sh" %}

# Load modules requested by user
{% for module in args.modules %}module load {{ module }} || printf "Could not load {{ module }}\n"
{% endfor %}

# Add variables to PATH
{% for path in paths %}export PATH={{ path }}:${PATH}
{% endfor %}

{% if docker %}{% include "templates/run_docker.sh" %}{% else %}{% include "templates/run_singularity.sh" %}{% endif %}
