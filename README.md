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
 
## Usage

First, you can clone the repository and install tunel! This can be done with pip.

```bash
$ git clone https://github.com/vsoch/tunel
$ cd tunel
$ pip install -e .
```

### Setup

Typically, setup is something you can do once and then will never need to do again.
For tunel, this means:

1. Adding a named entry to your ~/.ssh/config for your cluster(s) (if you don't have one already)
2. Tweaking the tunel settings, if needed.

#### SSH config

You will also need to at the minimum configure your ssh to recognize your cluster. Tunel takes a simple
approach of using a named configuration in your `~/.ssh/config` that can be re-used instead of asking you for a ussername
or password on the fly, and we do this to make it easy - you add the entry once and then forget about it.

Let's pretend we are logging into a cluster named sherlock (many clusters use this name, surprisingly!)
as a valid host. We have provided a [hosts folder](scripts/hosts) 
for helper scripts that will generate recommended ssh configuration snippets to put in your `~/.ssh/config` file. Based
on the name of the folder, you can intuit that the configuration depends on the cluster
host. Here is how you can generate this configuration for Sherlock:

```bash
bash scripts/hosts/sherlock_ssh.sh
```
```
Host sherlock
    User put_your_username_here
    Hostname sh-ln01.stanford.edu
    GSSAPIDelegateCredentials yes
    GSSAPIAuthentication yes
    ControlMaster auto
    ControlPersist yes
    ControlPath ~/.ssh/%l%r@%h:%p
```

The Hostname should be the one that you typically use when you ssh into your cluster,
and your username as well. By using these options can reduce the number of times you need to authenticate. 

As another example, here is a simple setup with a simple Host, Username, and custom port:

```
Host myserver
    User myuser
    Hostname myserver.home.network
    Port 92    
```

If you want to add a configuration file for a different host (or just
an example) please [open an issue](https://github.com/vsoch/tunel/issues) or pull request.
If you don't have a file in the location `~/.ssh/config` then you can generate it programatically:

```bash
$ /bin/bash scripts/hosts/sherlock_ssh.sh >> ~/.ssh/config
```

Do not run this command if there is content in the file that you might overwrite! 

#### Settings

Tunel has a default settings file at [tunel/settings.yml](tunel/settings.yml]) that you can tweak
on your local machine. The defaults should work for most, but we will detail some of the ones
that might need customization depending on your cluster.


### Isolated Compute Nodes

Depending on your cluster, you will need to identify whether the compute nodes (not the login nodes) are isolated from the outside world or not (i.e can be ssh'd into directly). This is important when we are setting up the ssh command to port forward from the local machine to the compute node. 

For HPC's where the compute node is isolated from the outside world, the ssh command basically establishes a tunnel to the login node, and then from the login node establishes another tunnel to the compute node. In this case we write a command where we port forward to the login node, and then the compute node, which is accessible from the login node. The entire command might look like this:

```bash
$ ssh -L $PORT:localhost:$PORT ${RESOURCE} ssh -L $PORT:localhost:$PORT -N "$MACHINE" &
```

In the command above, the first half is executed on the local machine `ssh -L $PORT:localhost:$PORT ${RESOURCE}`, which establishes a port forwarding to the login node. The next line `ssh -L $PORT:localhost:$PORT -N "$MACHINE" &` is run from the login node, and port forwards it to the compute node, since you can only access the compute node from the login nodes.

For HPC's where the compute node is not isolated from the outside world the ssh command for port forwarding first establishes a connection the login node, but then continues to pass on the login credentials to the compute node to establish a tunnel between the localhost and the port on the compute node. 
The ssh command in this case utilizes the flag `-K` which forwards the login credentials to the compute node:

```bash
$ ssh "$DOMAINNAME" -l $FORWARD_USERNAME -K -L  $PORT:$MACHINE:$PORT -N  &
```

The drawback of this method is that when tunel is run, you will have to authenticate twice (once at the beginning to check if a job is running on the HPC, and when the port forwarding is setup). For tunel, you can either hard code this in your [tunel/settings.yml](tunel/settings.yml) file, as `isolated_nodes: true/false` OR provide as a command line argument.

### Commands

Tunel is driven by a command line client, and (to be a developed) a web interface that allows the same functionality.

#### shell

The most basic thing you can do with tunel is to open an ssh tunnel. Arguably, you'd be just as well off using `ssh`, however
we provide the command as it logically fits with the tool. Let's say we've defined a server named "waffles" in our ~/.ssh/config.
We could do:

```bash
$ tunel shell waffles
```

#### exec

If you want to execute a command to a cluster (e.g., try listing files there, for example) you can use `exec`:

```bash
$ tunel exec waffles ls
```

#### tunnel

The simplest thing tunnel can do is if you already have a service running on your cluster or server (e.g., let's say we ssh in and start a web server) in one terminal:

```bash
$ tunel shell waffles
$ echo "<h1>Hello World</h1>" > index.html
$ python -m http.server 9999
```

We might want to open a tunel to this node from our local machine. That would look like this:

```bash
$ tunel tunnel waffles --port 9999
```

If we don't provide a `--local-port` it will default to 4000 (or the port you've added to your settings.yml).
Once you've done this, you should be able to open your local browser to 4000 and see the file from your server!

#### launch

Tunel has the concept of launchers, or a known cluster / HPC or server technology that can launch a service or job on your
behalf. While some of these are typical of HPC, many of them are not, and could be used on a personal server that you have.
Our launchers include:

**under development**

 - **singularity** run a singularity container on the server directly.
 - **docker** run a docker container on the server directly.
 - **slurm**: submit jobs (or applications) via SLURM, either a job or a service on a node to forward back.

#### singularity

Let's say you want to run a Singularity container on your remote server "waffles." You might do:

```bash
$ tunel run-singularity waffles docker://busybox echo hello
```
```
vanessa@dinoserver:~$ singularity exec docker://busybox echo hello
INFO:    Using cached SIF image
hello
```

More coming soon!

## TODO

Create "tunel" command over
- should be in Python
- should be able to interact with itself on the cluster (hence the name tunel)
- should  be installed locally too (and maybe even allow installing itself via the cluster)
- should be able to interact with whatever APIs available on the cluster (and detect what is there?)
- should have suite of applications you can install (e.g., pull containers)
- so we need metadata for those containers - can they go in shpc?
- should tunel use shpc to pull / run containers, or just do on the fly?
- tunel alone should open UI that feels like cloud

## Developer Environemnts

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

### Writing Code

"I want to jump in and try stuff without friction. I just want to be able to start writing code and seeing what it does."

- Select what I need in an environment and be in it
- Comfortable interaction with logging in / browsing files / writing code
- Easy / nice interface to launch and monitor jobs
- (not totally necessary) CI integrated with development environment

## Deployment
You should clone the repo, and build the container (or you can also just clone and then use docker-compose and it will be pulled from Docker Hub).


```bash
git clone https://github.com/singularityhub/singularity-tunel
cd singularity-tunel
docker build -t vanessa/tunel .
```

## Deployment
You can use docker compose to deploy:

```bash          
docker-compose up -d
```
and then go to `127.0.0.1` (localhost).


## Endpoints
Here are some useful endpoints:

### Views
 - `/`: the root will show all containers available. When the user selects, he/she is taken to a screen to see input arguments. 
 - `/containers/random`: will return a random container
 - `/container/container.img`: will show metadata about a container.

### API
The following are considered API, meaning they return a text or json response, not intended for the user to interact with.

 - `/api/containers`: a list of all available containers
 - `/api/container/<string:name>`: a json object with container args, labels, and links.
 - `/api/container/args/<string:name>`: json of just container args
 - `/api/container/labels/<string:name>`: json of juist container labels
 - `/container/run/container.img`: Is the base for running a container, this one would be container.img. Arguments can be added as POST (eg, `?name=Amy`)
