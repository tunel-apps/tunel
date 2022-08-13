---
layout: app
name:  "singularity/socket/tunel-django"
launcher: "singularity"
script: "app.sh"
maintainer: "@vsoch"
github: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/singularity/socket/tunel-django/app.yaml"
script_url: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/singularity/socket/tunel-django/app.sh"
updated_at: "2022-08-13 13:14:24.703358"
description: "An example Django application run via a Singularity container."
config: {'launcher': 'singularity', 'script': 'app.sh', 'description': 'An example Django application run via a Singularity container.', 'needs': {'socket': True}, 'examples': '# Run app on login node with singularity, custom tag dev\ntunel run-app waffles singularity/socket/tunel-django --tag=dev\n# Force a new pull\ntunel run-app waffles singularity/socket/tunel-django --tag=dev --pull\n# Set a custom user/password (note that the UI is only available to you so this is not for security)\ntunel run-app waffles singularity/socket/tunel-django --tag=dev --user=hello --pass=moto  \n', 'args': [{'name': 'user', 'description': 'username for logging into Django app (NOT your cluster username), defaults to tunel-user'}, {'name': 'pass', 'description': 'password for logging in to Django app (NOT your cluster password), defaults to tunel-pass'}, {'name': 'workdir', 'description': 'Working directory for app (and to show file explorer for)'}, {'name': 'container', 'description': 'Change the app container used (default is demo ghcr.io/tunel-apps/tunel-django). Must start with container URI to pull (e.g., docker://)'}, {'name': 'tag', 'description': 'Tag of the container to use (defaults to latest)'}, {'name': 'pull', 'description': 'force a new pull (even if the container already exists).'}]}
---

### Usage

```bash
$ tunel run-app <server> singularity/socket/tunel-django
```


#### Arguments

<div class="fresh-table">
<table class="table">
<thead>
  <th>Name</th>
  <th>Description</th>
  <th>Split By</th>
</thead>
<tbody>
<tr>
   <td>user</td>
   <td>username for logging into Django app (NOT your cluster username), defaults to tunel-user</td>
   <td>NA</td>
</tr>
<tr>
   <td>pass</td>
   <td>password for logging in to Django app (NOT your cluster password), defaults to tunel-pass</td>
   <td>NA</td>
</tr>
<tr>
   <td>workdir</td>
   <td>Working directory for app (and to show file explorer for)</td>
   <td>NA</td>
</tr>
<tr>
   <td>container</td>
   <td>Change the app container used (default is demo ghcr.io/tunel-apps/tunel-django). Must start with container URI to pull (e.g., docker://)</td>
   <td>NA</td>
</tr>
<tr>
   <td>tag</td>
   <td>Tag of the container to use (defaults to latest)</td>
   <td>NA</td>
</tr>
<tr>
   <td>pull</td>
   <td>force a new pull (even if the container already exists).</td>
   <td>NA</td>
</tr>

</tbody></table></div>

<br>

If split by is provided, this means the argument takes a list, and you should use this as a delimiter.




#### Needs

  - socket



### Examples

```bash
# Run app on login node with singularity, custom tag dev
tunel run-app waffles singularity/socket/tunel-django --tag=dev
# Force a new pull
tunel run-app waffles singularity/socket/tunel-django --tag=dev --pull
# Set a custom user/password (note that the UI is only available to you so this is not for security)
tunel run-app waffles singularity/socket/tunel-django --tag=dev --user=hello --pass=moto  
```


### Scripts

> app.sh

This app uses the singularity launcher and the following script:

```bash
{% raw %}#!/bin/bash

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
{% endraw %}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/tunel-apps/tunel/issues)
