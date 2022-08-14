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
echo "App working directory is ${WORKDIR}"

# Remove socket if exists
{% include "bash/socket/set-socket.sh" %}

# Load modules requested by user
{% for module in args.modules %}module load {{ module }} || printf "Could not load {{ module }}\n"
{% endfor %}

# Add variables to PATH
{% for path in paths %}export PATH={{ path }}:${PATH}
{% endfor %}

# Just pull to tmp for now so cleaned up
SIF="${SINGULARITY_CACHEDIR}/code-server.sif"
CONTAINER="docker://codercom/code-server:{% if args.tag %}{{ args.tag }}{% else %}latest{% endif %}"

# First effort
if command -v singularity &> /dev/null
then
    printf "singularity pull ${CONTAINER}\n"

    mkdir -p ${SOCKET_DIR}/home

    # Only pull the container if we do not have it yet, or the user requests it
    if [[ ! -f "${SIF}" ]] || [[ "{{ args.pull }}" != "" ]]; then
        singularity pull --force ${SIF} ${CONTAINER}
    fi    
    printf "singularity run --home ${SOCKET_DIR}/home --bind ${WORKDIR}:/home/coder/project ${SIF} --socket ${SOCKET}\n"
    singularity run --home ${SOCKET_DIR}/home --bind ${WORKDIR}:/home/coder/project ${SIF} --socket ${SOCKET}
else
    printf "Singularity is not available.\n"
fi
