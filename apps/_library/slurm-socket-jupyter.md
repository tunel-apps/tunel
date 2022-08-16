---
layout: app
name:  "slurm/socket/jupyter"
launcher: "slurm"
script: "jupyter.sbatch"
maintainer: "@vsoch"
github: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/slurm/socket/jupyter/app.yaml"
script_url: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/slurm/socket/jupyter/jupyter.sbatch"
updated_at: "2022-08-15 17:56:48.532073"
description: "A Jupyter notebook intended to be run with a slurm job, interactive via a socket."
config: {'launcher': 'slurm', 'script': 'jupyter.sbatch', 'description': 'A Jupyter notebook intended to be run with a slurm job, interactive via a socket.', 'args': [{'name': 'workdir', 'description': 'Working directory for the notebook'}, {'name': 'jupyterlab', 'description': 'Try running jupyterlab instead (e,g. set to true to enable)'}, {'name': 'modules', 'description': 'comma separated list of modules to load', 'split': ','}], 'needs': {'socket': True}}
---

### Usage

```bash
$ tunel run-app <server> slurm/socket/jupyter
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
   <td>workdir</td>
   <td>Working directory for the notebook</td>
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




### Scripts

> jupyter.sbatch

This app uses the slurm launcher by default.

```bash
{% raw %}#!/bin/bash

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
{% endraw %}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/tunel-apps/tunel/issues)
