---
layout: app
name:  "slurm/socket/singularity-jupyter"
launcher: "slurm"
script: "jupyter.sbatch"
maintainer: "@vsoch"
github: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/slurm/socket/singularity-jupyter/app.yaml"
script_url: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/slurm/socket/singularity-jupyter/jupyter.sbatch"
updated_at: "2022-08-13 13:14:24.684516"
description: "A jupyter notebook (or lab) intended to be run in a Singularity container."
config: {'launcher': 'slurm', 'script': 'jupyter.sbatch', 'description': 'A jupyter notebook (or lab) intended to be run in a Singularity container.', 'args': [{'name': 'jupyterlab', 'description': 'Try running jupyterlab instead (e,g. set to true to enable)'}, {'name': 'workdir', 'description': 'Working directory for the notebook'}, {'name': 'modules', 'description': 'comma separated list of modules to load', 'split': ','}], 'needs': {'socket': True}}
---

### Usage

```bash
$ tunel run-app <server> slurm/socket/singularity-jupyter
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
   <td>jupyterlab</td>
   <td>Try running jupyterlab instead (e,g. set to true to enable)</td>
   <td>NA</td>
</tr>
<tr>
   <td>workdir</td>
   <td>Working directory for the notebook</td>
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




### Scripts

> jupyter.sbatch

This app uses the slurm launcher and the following script:

```bash
{% raw %}#!/bin/bash

JOB_NAME="{{ jobname }}"
SOCKET_DIR="{{ scriptdir }}"
mkdir -p ${SOCKET_DIR}

# Include Singularity cachedir if not set
{% include "bash/singularity/set-cache-tmp.sh" %}

# Working Directory
NOTEBOOK_DIR={% if args.workdir %}{{ args.workdir }}{% else %}$HOME{% endif %}
cd $NOTEBOOK_DIR

echo "Job is ${JOB_NAME}"
echo "Socket directory is ${SOCKET_DIR}"
echo "Notebook working directory is ${NOTEBOOK_DIR}"

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
SIF="${SINGULARITY_CACHEDIR}/datascience-notebook.sif"
CONTAINER="{% if args.container %}{{ args.container }}{% else %}docker://jupyter/datascience-notebook{% endif %}"

# First effort
if command -v singularity &> /dev/null
then
    printf "singularity pull ${SIF} ${CONTAINER}\n"
    singularity pull ${SIF} ${CONTAINER}

    # In case doesn't exist yet
    mkdir -p $HOME/.jupyter

    printf "singularity exec --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local ${CONTAINER} jupyter notebook --no-browser --sock ${SOCKET}\n"
    singularity exec {% if args.jupyterlab %}--env JUPYTER_ENABLE_LAB=yes{% endif %} --home ${HOME} --bind ${HOME}/.local:/home/jovyan/.local --bind ${HOME}/.jupyter:/home/jovyan/.jupyter "${CONTAINER}" jupyter {% if args.jupyterlab %}lab{% else %}notebook{% endif %} --no-browser --sock ${SOCKET}
else
    printf "Singularity is not available.\n"
fi
{% endraw %}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/tunel-apps/tunel/issues)
