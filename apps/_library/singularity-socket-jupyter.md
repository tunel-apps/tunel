---
layout: app
name:  "singularity/socket/jupyter"
launcher: "singularity"
script: "jupyter.sh"
maintainer: "@vsoch"
github: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/singularity/socket/jupyter/app.yaml"
script_url: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/singularity/socket/jupyter/jupyter.sh"
updated_at: "2022-08-14 12:59:18.922122"
description: "A singularity jupyter notebook or lab to run directly on a remote (e.g., head node)"
config: {'launcher': 'singularity', 'script': 'jupyter.sh', 'description': 'A singularity jupyter notebook or lab to run directly on a remote (e.g., head node)', 'needs': {'socket': True}, 'examples': '# Run jupyter notebook on login node with custom container\ntunel run-app waffles singularity/socket/jupyter --container=docker://jupyter/datascience-notebook\n# Run Jupyterlab login node (via Singularity container) on open science grid\ntunel run-app osg singularity/socket/jupyter --jupyterlab=true\n', 'args': [{'name': 'container', 'description': 'Change the jupyter container used (default is datascience notebook). Must start with container URI to pull (e.g., docker://)'}, {'name': 'jupyterlab', 'description': 'Try running jupyterlab instead (e,g. set to true to enable)'}, {'name': 'modules', 'description': 'comma separated list of modules to load', 'split': ','}]}
---

### Usage

```bash
$ tunel run-app <server> singularity/socket/jupyter
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
   <td>container</td>
   <td>Change the jupyter container used (default is datascience notebook). Must start with container URI to pull (e.g., docker://)</td>
   <td>NA</td>
</tr>
<tr>
   <td>jupyterlab</td>
   <td>Try running jupyterlab instead (e,g. set to true to enable)</td>
   <td>NA</td>
</tr>
<tr>
   <td>modules</td>
   <td>comma separated list of modules to load</td>
   <td>,</td>
</tr>

</tbody></table></div>

<br>

If split by is provided, this means the argument takes a list, and you should use this as a delimiter.




#### Needs

  - socket



### Examples

```bash
# Run jupyter notebook on login node with custom container
tunel run-app waffles singularity/socket/jupyter --container=docker://jupyter/datascience-notebook
# Run Jupyterlab login node (via Singularity container) on open science grid
tunel run-app osg singularity/socket/jupyter --jupyterlab=true
```


### Scripts

> jupyter.sh

This app uses the singularity launcher by default.

```bash
{% raw %}#!/bin/bash

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

# Just pull to tmp for now so cleaned up
SIF="${SINGULARITY_CACHEDIR}/jupyter-notebook.sif"
CONTAINER="{% if args.container %}{{ args.container }}{% else %}docker://jupyter/datascience-notebook{% endif %}"

# First effort
if command -v singularity &> /dev/null
then
    printf "singularity pull ${CONTAINER}\n"

    # Only pull the container if we do not have it yet
    if [[ ! -f "${SIF}" ]]; then
        singularity pull ${SIF} ${CONTAINER}
    fi

    # In case they don't exist yet
    mkdir -p $HOME/.jupyter

    printf "singularity exec {% if args.jupyterlab %}--env JUPYTER_ENABLE_LAB=yes{% endif %} --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local ${CONTAINER} jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --sock ${SOCKET}\n"
    singularity exec {% if args.jupyterlab %}--env JUPYTER_ENABLE_LAB=yes{% endif %} --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local --bind ${HOME}/.jupyter:/home/jovyan/.jupyter "${SIF}" jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --sock ${SOCKET}
else
    printf "Singularity is not available.\n"
fi
{% endraw %}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/tunel-apps/tunel/issues)
