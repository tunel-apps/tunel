---
layout: app
name:  "htcondor/job"
launcher: "htcondor"
script: "job.sh"
maintainer: "@vsoch"
github: "https://github.com/vsoch/tunel/blob/main/tunel/apps/htcondor/job/app.yaml"
script_url: "https://github.com/vsoch/tunel/blob/main/tunel/apps/htcondor/job/job.sh"
updated_at: "2022-07-20 14:32:01.503643"
description: "A simple example to launch an HTCondor job (to sleep)"
config: {'launcher': 'htcondor', 'description': 'A simple example to launch an HTCondor job (to sleep)', 'script': 'job.sh', 'args': [{'name': 'cpus', 'description': 'The number of CPUs to allocate for the job (defaults to 1)'}, {'name': 'memory', 'description': 'The memory (in MB, without writing MB) for the job'}, {'name': 'disk', 'description': 'The disk space (also in GB, without the GB suffix) for the job'}, {'name': 'njobs', 'description': 'The number of jobs to launch of this type (defaults to 1)'}]}
---

### Usage

```bash
$ tunel run-app <server> htcondor/job
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
   <td>cpus</td>
   <td>The number of CPUs to allocate for the job (defaults to 1)</td>
   <td>NA</td>
</tr>
<tr>
   <td>memory</td>
   <td>The memory (in MB, without writing MB) for the job</td>
   <td>NA</td>
</tr>
<tr>
   <td>disk</td>
   <td>The disk space (also in GB, without the GB suffix) for the job</td>
   <td>NA</td>
</tr>
<tr>
   <td>njobs</td>
   <td>The number of jobs to launch of this type (defaults to 1)</td>
   <td>NA</td>
</tr>

</tbody></table></div>

<br>

If split by is provided, this means the argument takes a list, and you should use this as a delimiter.







### Scripts

> job.sh

This app uses the htcondor launcher and the following script:

```bash
{% raw %}#!/bin/bash 
# job.sh: a short discovery job 
# This is part of the OSG tutorial-quickstart
printf "Start time: "; /bin/date 
printf "Job is running on node: "; /bin/hostname 
printf "Job running as user: "; /usr/bin/id 
printf "Job is running in directory: "; /bin/pwd 
echo
echo "Working hard..."
sleep 30
echo "Science complete!"
{% endraw %}
```

Have any questions, or want to request a new app or launcher? [Ask us!](https://github.com/vsoch/tunel/issues)
