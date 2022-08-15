---
layout: app
name:  "slurm/port/jupyter"
launcher: "slurm"
script: "jupyter.sbatch"
maintainer: "@vsoch"
github: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/slurm/port/jupyter/app.yaml"
script_url: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/slurm/port/jupyter/jupyter.sbatch"
updated_at: "2022-08-15 17:56:48.536849"
description: "A Jupyter notebook intended to be run with a slurm job, interactive via a port"
config: {'launcher': 'slurm', 'script': 'jupyter.sbatch', 'description': 'A Jupyter notebook intended to be run with a slurm job, interactive via a port', 'args': [{'name': 'workdir', 'description': 'Working directory for the notebook'}, {'name': 'jupyterlab', 'description': 'Try running jupyterlab instead (e,g. set to true to enable)'}, {'name': 'modules', 'description': 'comma separated list of modules to load', 'split': ','}]}
---

### Usage

```bash
$ tunel run-app <server> slurm/port/jupyter
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







### Scripts

> jupyter.sbatch

This app uses the slurm launcher by default.

```bash
{% raw %}#!/bin/bash

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
{% endraw %}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/tunel-apps/tunel/issues)
