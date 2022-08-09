# Tunel

Developer tools for HPC. Because we can't have cloud but we want nice things too.

## Introduction

Tunel will do exactly that - create a tunel between your local workstation and an HPC cluster
to try and abstract away some of the complexity of launching interfaces that feel a bit more modern.
In its simplest form this means:

 1. Installing tunel locally and discovering what is available on your cluster
 2. Running a local server (or via the command line) selecting and configuring an application to run.
 3. Launching it via a ssh tunnel to your cluster resource
 4. Getting back an address to open up and start working.

See our ⭐️ [documentation](https://tunel-apps.github.io/tunel) ⭐️ to get started. 

## TODO
  
Should there be an init/check command that sniffs what is available on a cluster? E.g., singularity, sbatch, sinfo, module load, etc.
Create "tunel" command over

- should be able to interact with whatever APIs available on the cluster (and detect what is there?)
- tunel alone should open UI that feels like cloud

## Developer Environments

Request a node, akin to cloud - come up with standard sizes (and can we sniff slurm conf for this too?) and then
offer a UI to deploy!

## Developer Workflows

In developing this tool, I decided to sit down and write exactly what I wanted, and then (hopefully) to see if there would
be a way to implement it given the resources of the HPC clusters I have access to. The interesting observation is that in most of these
cases, compute wasn't a huge issue, but rather:

1. consistency in environments
2. only having command line (and not a UI access)
3. no ability to interact with APIs.

So this spawned the idea for tunel - could I, despite working in HPC, be able to provide APIs and interfaces regardless?

### Monitoring

Launch interface for slurm and monitoring jobs (probably can attach to login node?)

### Running Workflows

Ability to launch different workflow managers? E.g., snakemake? Does it make sense to have an organization of running apps 
akin to containers running to manage things? E.g., $SCRATCH/tunel/$CONTAINER?

More generally (notes from HPC Huddle Slack)

- A workflow management system available on the system
- Example: https://pegasus.isi.edu/
- The WfMS is readily available on many systems so I can easily run my work on different machines.

### Writing Code

"I want to jump in and try stuff without friction. I just want to be able to start writing code and seeing what it does."

- Select what I need in an environment and be in it
- Comfortable interaction with logging in / browsing files / writing code
- Easy / nice interface to launch and monitor jobs
- (not totally necessary) CI integrated with development environment

### APIs

- A scripting language API for interacting programmatically with the scheduler
 - submit, query status, and remove jobs
 - query available resources
 - parser for job history & logs information
 - syntax and documentation that are not just for system administrators: PySlurm needs work in this regard

#### Modules / Containers

- Containerized cluster
 - Enables new users to learn how to interact with a scheduler in a (safer) local environment
 - Test small workflows locally before porting to a big machine
 - Can be used for teaching ala Binder
 - HTCondor provides containers for both individual daemons and full systems
 - There are examples of PBS and Slurm (& maybe others) out there but none of these others seem project supported.
