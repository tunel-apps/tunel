#!/bin/bash

JOB_NAME="{{ jobname }}"
SOCKET_DIR="{{ scriptdir }}"
mkdir -p ${SOCKET_DIR}

# Include Singularity cachedir if not set
{% include "bash/singularity/set-cache-tmp.sh" %}

# Set WORKDIR, first to args.workdir, then settings.yml workdir, then $HOME
{% include "bash/set-workdir.sh" %}
cd $WORKDIR

echo "Job is ${JOB_NAME}"
echo "Socket directory is ${SOCKET_DIR}"
echo "App working directory is ${WORKDIR}"

# Create .local folder for default modules, if doesn't exist
{% include "bash/python/create-local.sh" %}

# Remove socket if exists
{% include "bash/socket/set-socket.sh" %}

# Bind the database
DB_DIR=${SOCKET_DIR}/db
STATIC_DIR=${SOCKET_DIR}/static

# username and password for django to create
{% include "bash/set-user-pass.sh" %}

# Load modules requested by user
{% for module in args.modules %}module load {{ module }} || printf "Could not load {{ module }}\n"
{% endfor %}

# Add variables to PATH
{% for path in paths %}export PATH={{ path }}:${PATH}
{% endfor %}

# Just pull to tmp for now so cleaned up
SIF="${SINGULARITY_CACHEDIR}/tunel-django.sif"
CONTAINER="{% if args.container %}{{ args.container }}{% else %}docker://ghcr.io/tunel-apps/tunel-django:{% if args.tag %}{{ args.tag }}{% else %}latest{% endif %}{% endif %}"

# First effort
if command -v singularity &> /dev/null
then
    printf "singularity pull ${CONTAINER}\n"

    mkdir -p ${DB_DIR} ${STATIC_DIR}

    # Only pull the container if we do not have it yet, or the user requests it
    if [[ ! -f "${SIF}" ]] || [[ "{{ args.pull }}" != "" ]]; then
        singularity pull --force ${SIF} ${CONTAINER}
    fi
    
    # The false at the end ensures we aren't using nginx, but rather uwsgi just with sockets
    printf "singularity exec --bind ${DB_DIR}:/code/db --env TUNEL_PASS=***** --env TUNEL_USER=${TUNEL_USER} --bind ${WORKDIR}:/code/data ${SIF} /bin/bash /code/scripts/run_uwsgi.sh ${SOCKET} false\n"
    # The bind for WORKDIR to /var/www/data ensures the filesystem explorer works
    singularity exec --bind ${DB_DIR}:/code/db --env TUNEL_PASS=${TUNEL_PASS} --env TUNEL_USER=${TUNEL_USER} --bind ${WORKDIR}:/code/static --bind ${WORKDIR}:/code/data ${SIF} /bin/bash /code/scripts/run_uwsgi.sh ${SOCKET} false
else
    printf "Singularity is not available.\n"
fi
