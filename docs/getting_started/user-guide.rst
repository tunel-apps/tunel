.. _getting_started-user-guide:

==========
User Guide
==========

Introduction
============

Tunel is named for what it does. "Tunel" is an elegant derivation of "tunnel" and will do exactly that - 
create a tunel between your local workstation and an HPC cluster. Tunel tries to abstract away some 
of the complexity of launching interfaces that feel a bit more modern.
In its simplest form this means:

 1. Installing tunel locally and discovering what is available on your cluster
 2. Running a local server (or via the command line) selecting and configuring an application to run.
 3. Launching it via a ssh tunnel to your cluster resource
 4. Getting back an address to open up and start working.

If you haven't read :ref:`getting_started-installation` you should do that first.
 
Setup
=====

Typically, setup is something you can do once and then will never need to do again.
For tunel, this means:

1. Adding a named entry to your ~/.ssh/config for your cluster(s) (if you don't have one already)
2. Tweaking the tunel settings, if needed.


SSH config
----------

You will also need to at the minimum configure your ssh to recognize your cluster. Tunel takes a simple
approach of using a named configuration in your `~/.ssh/config` that can be re-used instead of asking you for a username
or password on the fly, and we do this to make it easy - you add the entry once and then forget about it.
When you have it working correctly, this should work:

.. code-block:: console

    $ ssh <server>


This can be easily done with some configuration of your ssh config!
Let's pretend we are logging into a cluster named sherlock (many clusters use this name, surprisingly!)
as a valid host. We have provided a [hosts folder](scripts/hosts) 
for helper scripts that will generate recommended ssh configuration snippets to put in your `~/.ssh/config` file. Based
on the name of the folder, you can intuit that the configuration depends on the cluster
host. Here is how you can generate this configuration for Sherlock:


.. code-block:: console

    $ bash scripts/hosts/sherlock_ssh.sh


.. code-block:: console

    Host sherlock
        User put_your_username_here
        Hostname sh-ln01.stanford.edu
        GSSAPIDelegateCredentials yes
        GSSAPIAuthentication yes
        ControlMaster auto
        ControlPersist yes
        ControlPath ~/.ssh/%l%r@%h:%p


The Hostname should be the one that you typically use when you ssh into your cluster,
and your username as well. By using these options can reduce the number of times you need to authenticate. 
It's recommended to include the Control* directives, as they will keep a socket so you
can login/ssh easily without needing to authenticate every time.

As another example, here is a simple setup with a simple Host, Username, and custom port:

.. code-block:: console

    Host myserver
        User myuser
        Hostname myserver.home.network
        Port 92    


If you want to add a configuration file for a different host (or just
an example) please [open an issue](https://github.com/tunel-apps/tunel/issues) or pull request.
If you don't have a file in the location `~/.ssh/config` then you can generate it programatically:

.. code-block:: console

    $ /bin/bash scripts/hosts/sherlock_ssh.sh >> ~/.ssh/config


Do not run this command if there is content in the file that you might overwrite! 


Settings File
-------------

Tunel has a default settings file at ``tunel/settings.yml`` that you can tweak
on your local machine. The defaults should work for most, but we will detail some of the ones
that might need customization depending on your cluster. Settings includes the following:


.. list-table:: Settings
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - tunel_home
     - The directory on your local machine to write any local assets, e.g., "tunel" will be written here
     - ``$HOME`` locally
   * - tunel_remote_home
     - The directory on your remote to write "tunel" with scripts, sockets, and assets
     - ``$HOME`` on your remote
   * - tunel_spinner
     - Tunel spinner for logger (see `example spinners <https://asciinema.org/a/504268>`_)
     - dots
   * - tunel_remote_work
     - Working directory to use for notebooks or apps. If not set, can be set on command line with ``--workdir``
     - ``$HOME``
   * - tunel_remote_sockets
     - Specific directory for remote sockets
     - ``$HOME/.tunel``
   * - ssh_port
     - set a default port to use for ssh
     - 22
   * - shell
     - set a default shell
     - /bin/bash
   * - remote_port
     - remote port to use (this should be randomly generated unless set here)
     - unset
   * - local_port
     - local port to use (when mapping a notebook, etc.)
     - 7789
   * - ssh_config
     - Default ssh config to read from
     - ``~/.ssh/config``
   * - ssh_sockets
     - Default directory to store sockets
     - ``~/.ssh/sockets``
   * - apps_dirs
     - Additional directories with apps to add (searched in order here)
     - ``$default_apps`` (in tunel/apps)
   * - launchers.singularity.paths
     - Add these to the path (e.g., mksquashfs is here) (list)
     - ``- /usr/sbin``
   * - launchers.singularity.environment
     - key value pairs of environment variables
     - ``- HELLO=MOTO``
   * - launchers.slurm.paths
     - Add these to the path (e.g., mksquashfs is here) (list)
     - ``- /usr/sbin``
   * - launchers.slurm.memory
     - Default job memory to ask for
     - 8000
   * - launchers.slurm.time
     - Default job time to ask for
     - 3:00:00
   * - min_port
     - If random port selection used (random port is null) allow within this range
     - 90000
   * - max_port
     - If random port selection used (random port is null) allow within this range
     - 99999
   * - config_editor
     - Default config editor
     - vim


Singularity Containers
----------------------

Most scripts that use Singularity will attempt to load it as a module, and this won't error if it fails.
If you don't have it as a module, it's recommended to have singularity on your path, or loaded in your profile for slurm apps that use it
or the Singularity launcher. It's also recommended to export your cache directory to somewhere with more space:

.. code-block:: console

    $ export SINGULARITY_CACHEDIR=$SCRATCH/.singularity


If you have custom logic to use Singularity that isn't encompassed in these
two use cases, you can `let us know <https://github.com/tunel-apps/tunel>`_ to ask for help, or write a custom app yourself.


Connecting to Apps
------------------

Since we cannot reliably always have access to an exposed port, the main (suggested) way to run an app is using
a socket. Apps are organized according to using sockets or ports, and optionally launchers, e.g:


.. code-block:: console

    tunel/apps
    └── slurm
        ├── port
        │   └── jupyter
        │       ├── app.yaml
        │       └── jupyter.sbatch
        └── socket
            ├── jupyter
            │   ├── app.yaml
            │   └── jupyter.sbatch
            └── singularity-jupyter
                ├── app.yaml
                └── jupyter.sbatch


As a note, there are apps provided here intended to be used with ports, but the developer @vsoch is
not able to test them easily since she does not have access to any resources that allow open TCP ports. However,
if you find an issue, please open and (ideally) help debug to fix it up.


Commands
========

Tunel is driven by a command line client, and (to be a developed) a web interface that allows the same functionality.

list-apps
---------

The first thing you might want to do is see what apps are available.

.. code-block:: console

    $ tunel list-apps
                         Tunel Apps                                                                                      
    |---|----------------------------------|----------------------------------------|
    | # | Name                             | Launcher    |     Supported            |                                                         
    |---|----------------------------------|----------------------------------------|                                                               
    │ 0 │ socket/tunel-django              │ singularity │ docker|slurm|singularity │   
    │ 1 │ htcondor/job                     │ htcondor    │                 htcondor │   
    │ 2 │ slurm/socket/singularity-jupyter │ slurm       │                    slurm │   
    │ 3 │ slurm/socket/jupyter             │ slurm       │                    slurm │   
    │ 4 │ slurm/port/jupyter               │ slurm       │                    slurm │   
    │ 5 │ singularity/socket/code-server   │ singularity │              singularity │   
    │ 6 │ singularity/socket/jupyter       │ singularity │              singularity │   
    └───┴──────────────────────────────────┴─────────────┴──────────────────────────┘   

These are located in the ``tunel/apps`` directory, organized by directory
organization for uniqueness. As of version 0.0.14 of tunel, apps have support
for multiple launchers, with a default (shown above).


info
----

To get basic info for an app, just ask for it:

.. code-block:: console

    $ tunel info socket/tunel-django

This should generally show you accepted flags/arguments, along with examples for running.
Since paths can be long, you are also able to ask for a shortened name, and it must still be
unique with the set. E.g.,:

.. code-block:: console

    $ tunel info tunel-django

works the same! This convention is true for all subsequent commands.
You can also ask for json:

.. code-block:: console

    $ tunel info tunel-django --json


If you ask for a shortened name that matches more than one app, you'll see:

.. code-block:: console

    $ tunel info singularity
    Found 3 apps:
    slurm/socket/singularity-jupyter
    singularity/socket/jupyter
    singularity/socket/tunel-django
    Be more specific to disambiguate singularity!

And you should follow the instruction and be more specific.

run-app
-------

The most common command that likely you'll run (after you use info and list-apps to find an app) is run-app!
That might look like this:

.. code-block:: console

    $ tunel run-app waffles code-server

Additionally, if an app supports multiple launchers, you can ask for one that isn't the default:

.. code-block:: console

    $ tunel run-app waffles tunel-django --launcher slurm
    $ tunel run-app bh tunel-django --launcher docker


If you ask for a launcher that isn't supported (typically meaning it has not been tested)
you'll see:

.. code-block:: console

    $ tunel run-app osg code-server --launcher slurm
    Loading app singularity/socket/code-server...
    Launcher slurm has not been tested for app singularity/socket/code-server

This doesn't mean the launcher cannot be supported, but you should open an issue so @vsoch can test it out,
or add the launcher to the ``launchers_supported`` in the app.yaml and test and open a pull request with your results.

shell
-----

The most basic thing you can do with tunel is to open an ssh tunnel. Arguably, you'd be just as well off using `ssh`, however
we provide the command as it logically fits with the tool. Let's say we've defined a server named "waffles" in our ~/.ssh/config.
We could do:

.. code-block:: console

    $ tunel shell waffles


exec
----

If you want to execute a command to a cluster (e.g., try listing files there, for example) you can use `exec`:

.. code-block:: console

    $ tunel exec waffles ls


or with an environment variable:


.. code-block:: console

    $ tunel exec waffles echo '$HOME'


api-get
-------

When you have a tunel app running, if it exposes an API via socket, tunel provides Python functions
to be able to hit defined points in its API. As an example, if we start with the `Tunel Django Template <https://github.com/tunel-apps/tunel-django/>`_
that serves a basic jokes API, we can either go to `http://127.0.0:8000/api/joke/` to see a json response for a joke,
or we can do either:

.. code-block:: console

    $ tunel api-get --socket /tmp/test/tunel-django.sock.api.sock /api/joke/ --json
    {
        "text": "Two JavaScript developers walked into the variable `bar`. Ouch!",
        "author": "elijahmanor",
        "created": "09/10/2013",
        "tags": [
            "javascript"
        ],
        "rating": 3
    }

Or just plain text:

.. code-block:: console

    $ tunel api-get --socket /tmp/test/tunel-django.sock.api.sock /api/joke/
    {"text": "q. Why did Jason cover himself with bubble wrap? a. Because he wanted to make a cross-domain JSONP request.", "question": "Why did Jason cover himself with bubble wrap?", "answer": "Because he wanted to make a cross-domain JSONP request", "author": "elijahmanor", "created": "09/11/2013", "tags": ["javascript"], "rating": 5}

And this is how you would embed (in your Python applications) logic to interact with your Tunel app, either on your host (where the socket is tunneled)
or the HPC cluster (where the socket is written).


launch
------

Tunel has the concept of launchers, or a known cluster / HPC or server technology that can launch a service or job on your
behalf. While some of these are typical of HPC, many of them are not, and could be used on a personal server that you have.
Our launchers include:

 - **singularity** run a singularity container on the server directly.
 - **docker** run a docker container on the server directly.
 - **slurm**: submit jobs (or applications) via SLURM, either a job or a service on a node to forward back.
 - **condor**: submit jobs (or apps) to an HTCondor cluster.

Each launcher can be run via an app, meaning you do a ``run-app`` on an app.yaml that specifies the launcher,
and we also provide courtesy functions (e.g., ``run-singularity``). These might be removed at some point, not decided yet.


singularity
^^^^^^^^^^^

Let's say you want to run a Singularity container on your remote server "waffles." You might do:


.. code-block:: console

    $ tunel run-singularity waffles exec docker://busybox echo hello

The above provides your request to run (or exec, as shown above) to Singularity.


.. code-block:: console

    $ tunel run-singularity waffles exec docker://busybox echo hello
    INFO:    Converting OCI blobs to SIF format
    INFO:    Starting build...
    Getting image source signatures
    Copying blob sha256:3cb635b06aa273034d7080e0242e4b6628c59347d6ddefff019bfd82f45aa7d5
    Copying config sha256:03781489f3738437ae98f13df5c28cc98bbc582254cfbf04cc7381f1c2ac1cc0
    Writing manifest to image destination
    Storing signatures
    2021/12/10 13:56:01  info unpack layer: sha256:3cb635b06aa273034d7080e0242e4b6628c59347d6ddefff019bfd82f45aa7d5
    2021/12/10 13:56:01  warn xattr{home} ignoring ENOTSUP on setxattr "user.rootlesscontainers"
    2021/12/10 13:56:01  warn xattr{/tmp/build-temp-105506159/rootfs/home} destination filesystem does not support xattrs, further warnings will be suppressed
    INFO:    Creating SIF file...
    hello


For this launcher, if your cluster doesn't have defaults for ``SINGULARITY_CACHEDIR`` (or other environment variables)
or things on the path, you can customize the settings.yml to add them. Take a look at the `launchers -> singularity` section
to customize. Finally, you can even start an interactive shell directly into a container!

.. code-block:: console

    $ tunel run-singularity waffles shell docker://busybox
    INFO:    Using cached SIF image
    Singularity> 


docker
^^^^^^

To run a docker container on your remote (likely a VM):

.. code-block:: console

    $ tunel run-docker waffles ubuntu



slurm
^^^^^

The most basic command for the slurm launcher is to get an interactive node, as follows:


.. code-block:: console

    $ tunel run-slurm waffles
    No command supplied, will init interactive session!
    (base) bash-4.2$ 
    
Let's say that you run an app (described below) that launches a slurm job to generate a job named `slurm-jupyter`. Here is how you'd kill it:

.. code-block:: console
   
    $ tunel stop-slurm oslic slurm-jupyter
    No command supplied, will init interactive session!
    (base) bash-4.2$ 


HTCondor
^^^^^^^^

To get an interactive node via HTCondor:


.. code-block:: console

    $ tunel run-condor osg
    No command supplied, will init interactive session!
    (base) bash-4.2$ 

You can also run a specific command to hit the head node:

    $ tunel run-condor osg ls
    tunel
    tutorial-quickstart
    
To launch a job, you can use an app that has a particular submission script provided:

.. code-block:: console
   
    $ tunel run-app osg htcondor/job

For any HTCondor job, you can customize the following on the fly as an argument:

 - **njobs**: the number of jobs to queue (defaults to 1 if unset)
 - **memory**: MB of memory, without "MB" (defaults to 1 MB)
 - **disk**: MB of disk space, also without MB (defaults to 1 MB)
 - **cpus**: number of CPUs to request (defaults to 1)


For example:

.. code-block:: console

    $ tunel run-app osg htcondor/job --cpus=1 --disk=1 --njobs=1

And then to stop a job:

.. code-block:: console

    $ tunel stop-condor osg htcondor-job

.. ::note

    This only adds basic functionality - a Singularity interactive notebook has been tested
    but @vsoch doesn't have a full HTCondor cluster (that allows interactive jobs) to fully
    test interactive apps! If you can help here, please do! Additionally, we plan to update
    this launcher to take advantage of the HTCondor Python API (if reasonable to do).


tunnel
------

.. ::note

    **Note** this was originally developed and needs more work to function with sockets!
    @vsoch is planning to provide simple app templates that will come ready to go with either
    a port or a socket so you might not need this command. If you have a use case that warrants
    this command, please open an issue so @vsoch can work on it.

If you are able to open ports, the simplest thing tunnel can do is if you already have a service running on your cluster or server (e.g., let's say we ssh in and start a web server) in one terminal:


.. code-block:: console

    $ tunel shell waffles
    $ echo "<h1>Hello World</h1>" > index.html
    $ python -m http.server 9999
    
    
We might want to open a tunel to this node from our local machine. That would look like this:


.. code-block:: console

    $ tunel tunnel waffles --port 9999


If we don't provide a ``--local-port`` it will default to 4000 (or the port you've added to your settings.yml).
Once you've done this, you should be able to open your local browser to 4000 and see the file from your server!


Apps
====

A tunel app is identified by a yaml file, app.yaml, in an install directory (which it is suggested
you namespace to make it easy to identify). By default in the tunel settings.yml, you'll notice one
default apps directory:

.. code-block:: yaml

    apps_dir:
      - $default_apps


This defaults to ``tunel/apps`` and it looks something like this:

.. code-block:: console

    $ tree tunel/apps/slurm/
    tunel/apps/slurm/
    ├── port
    │   └── jupyter
    │       ├── app.yaml
    │       └── jupyter.sbatch
    └── socket
        └── jupyter
            ├── app.yaml
            └── jupyter.sbatch
    
Notice that apps are organized into being accessible via port (not recommended) vs. socket.
If you need to use a socket, the app will have needs->socket->true. Socket enabled apps will
start the job, show you two options for ssh commands to connect when the notebook is ready (e.g., when the output
shows up with the token) and then you can copy paste that into a separate terminal to start the tunnel.
This might be possible to do on your behalf, but I like the user having control of when to start / stop it
so this is the current design. It will ask you for your password, and if you don't want to do that,
try adding your rsa keys to the authorized_keys file in your ~/.ssh directory on your cluster (thanks to `@becker33 <https://github.com/becker33>`_ for this tip)!

workdir
^^^^^^^

Tunel has a special setup for working directory:

1. If you set ``--workdir`` on the command line (and the app uses it in its template) it will use this.
2. Otherwise, set ``tunel_remote_work`` in your settings.yaml to set a more global working directory.
3. The default working directory, given nothing else is set, is ``$HOME``


app arguments
^^^^^^^^^^^^^

Apps can be customized with arguments. For example, the ``singularity/port/jupyter`` app can run a jupyter notebook,
with a default jupyter container, or one that you select with container:

.. code-block:: console

    $ tunel run-app waffles singularity/port/jupyter --container=docker://jupyter/datascience-notebook

For the above, since it's for a Singularity container we provide the full unique resource identifier with ``docker://``.
Also note that app arguments *must* start with two slashes.


More Detail
^^^^^^^^^^^

Each app.yaml (the path of the running app that we've chosen in tunel/apps) is going to specify a launcher (e.g., slurm or singularity)
along with different parameters that are needed. After launch, in the case of slurm you'll see the above execute commands to 
interact with the launcher, and then go into an exponential backoff while waiting for a node. When finished, the above will 
launch a job with an interactive notebook and return the connection information. Note that you should watch the error and output logs
(in purple and cyan, respectively) to determine when the application is ready to connect to. E.g.,
a Singularity container will likely need to be pulled, and then converted to SIF, which unfortunately isn't quick. 
When it's ready, try connecting. This command generally works by finding the app.yaml under apps/slurm/jupyter in the default directory,
an each app.yaml will define it's own launcher and other needs for running.


Troubleshooting
===============

Error Messages
--------------

If you have extra configuration that can output an error (e.g., "X11 request not supported" this could cause an issue as tunel
is parsing output from ssh. To fix this, you can typically remove the offending setting (e.g., tunel does not need X11 forwarding to work!)
However if you find there is some printed command that is breaking tunel, please open an issue and we can find a fix.

My Slurm Job Isn't Being Allocated!
-----------------------------------

This happened to me once! I was trying to launch a slurm + singularity app on a cluster that didn't have Singularity.
The best thing to check is the error and output logs, and there is typically a command printed to the console for how you can do that:


.. code-block:: console

    ssh brainhack cat /home/opc/tunel/slurm/socket/tunel-django/app.sh.out
    ssh brainhack cat /home/opc/tunel/slurm/socket/tunel-django/app.sh.err
    

Custom Path Logic
-----------------

For most apps, we assume that you can either add a module to load to your settings modules, or it's available  on your
cluster without loading. For clusters where this isn't the case, most apps that run on a login node (meaning the bash profile won't be sourced by
default) will source either ``~/.bash_profile`` or  ``~/.profile`` for you. If you find a case where this isn't done, or isn't done to your
needs, please open an issue.

Open Failed Error
-----------------

If you see:

.. code-block:: console

    open failed: administratively prohibited: open failed
 
This typically means your cluster doesn't allow forwarding (most that I've encountered do, and the only time I hit this case was
when I had set up my own cluster and didn't know I needed to do this!) You can read `more about the error here <https://unix.stackexchange.com/questions/14160/ssh-tunneling-error-channel-1-open-failed-administratively-prohibited-open>`_.

TLDR: to fix you need to set

.. code-block:: console

    sudo vi /etc/ssh/sshd_config

    AllowAgentForwarding yes
    AllowTcpForwarding yes
    X11Forwarding yes
    X11UseLocalhost no

    sudo systemctl restart sshd


In your ``/etc/ssh/sshd_config`` on the login and worker nodes. And don't forget to restart!

.. code-block:: console

    sudo systemctl restart ssh
    

