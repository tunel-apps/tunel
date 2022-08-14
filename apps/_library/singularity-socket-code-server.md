---
layout: app
name:  "singularity/socket/code-server"
launcher: "singularity"
script: "app.sh"
maintainer: "@vsoch"
github: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/singularity/socket/code-server/app.yaml"
script_url: "https://github.com/tunel-apps/tunel/blob/main/tunel/apps/singularity/socket/code-server/app.sh"
updated_at: "2022-08-14 12:59:18.917422"
description: "Work on files on your remote machine via VS Code in the browser, all via unix sockets"
config: {'launcher': 'singularity', 'script': 'app.sh', 'description': 'Work on files on your remote machine via VS Code in the browser, all via unix sockets', 'needs': {'socket': True}, 'examples': '# Run app on login node with singularity, shorter pattern match\ntunel run-app waffles code-server\ntunel run-app waffles singularity/socket/code-server\n', 'commands': {'post': 'cat $socket_dir/home/.config/code-server/config.yaml'}, 'args': [{'name': 'workdir', 'description': 'Working directory for app (and to show file explorer for)'}, {'name': 'container', 'description': 'Change the app container used (default is demo ghcr.io/tunel-apps/tunel-django). Must start with container URI to pull (e.g., docker://)'}, {'name': 'tag', 'description': 'Tag of the container to use (defaults to latest)'}, {'name': 'pull', 'description': 'force a new pull (even if the container already exists).'}]}
---

### Usage

```bash
$ tunel run-app <server> singularity/socket/code-server
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
# Run app on login node with singularity, shorter pattern match
tunel run-app waffles code-server
tunel run-app waffles singularity/socket/code-server
```


### Scripts

> app.sh

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
{% endraw %}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/tunel-apps/tunel/issues)
