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
an example) please [open an issue](https://github.com/vsoch/tunel/issues) or pull request.
If you don't have a file in the location `~/.ssh/config` then you can generate it programatically:

.. code-block:: console

    $ /bin/bash scripts/hosts/sherlock_ssh.sh >> ~/.ssh/config


Do not run this command if there is content in the file that you might overwrite! 


Settings File
-------------

Tunel has a default settings file at [tunel/settings.yml](tunel/settings.yml]) that you can tweak
on your local machine. The defaults should work for most, but we will detail some of the ones
that might need customization depending on your cluster.

Singularity Containers
----------------------

Most scripts that use Singularity will attempt to load it as a module, and this won't error if it fails.
If you don't have it as a module, it's recommended to have singularity on your path, or loaded in your profile for slurm apps that use it
or the Singularity launcher. It's also recommended to export your cache directory to somewhere with more space:

.. code-block:: console

    $ export SINGULARITY_CACHEDIR=$SCRATCH/.singularity


If you have custom logic to use Singularity that isn't encompassed in these
two use cases, you can [let us know](https://github.com/vsoch/tunel) to ask for help, or write a custom app yourself.

Connecting to Apps
------------------

Since we cannot reliably always have access to an exposed port, the main (suggested) way to run an app is using
a socket. Apps are organized according to using sockets or ports, e.g:


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

    $ tunel exec waffles echo `$HOME`


tunnel
------

.. ::note

    **Note** this was originally developed and needs more work to function with sockets!
    @vsoch is planning to provide simple app templates that will come ready to go with either
    a port or a socket so you might not need this command.

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

launch
------

Tunel has the concept of launchers, or a known cluster / HPC or server technology that can launch a service or job on your
behalf. While some of these are typical of HPC, many of them are not, and could be used on a personal server that you have.
Our launchers include:

 - **singularity** run a singularity container on the server directly.
 - **docker** run a docker container on the server directly.
 - **slurm**: submit jobs (or applications) via SLURM, either a job or a service on a node to forward back.


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


slurm
^^^^^

The most basic command for the slurm launcher is to get an interactive node, as follows:


.. code-block:: console

    $ tunel run-slurm waffles
    No command supplied, will init interactive session!
    (base) bash-4.2$ 
    
Let's say that you run an app [described below](#apps) that launches a slurm job to generate a job named `slurm-jupyter`. Here is how you'd kill it:

.. code-block:: console
   
    $ tunel stop-slurm oslic slurm-jupyter
    No command supplied, will init interactive session!
    (base) bash-4.2$ 


More coming soon!

apps
----

A tunel app is identified by a yaml file, app.yaml, in an install directory (which it is suggested
you namespace to make it easy to identify). By default in the tunel settings.yml, you'll notice one
default apps directory:

.. code-block:: yaml

    apps_dir:
      - $default_apps


This defaults to [tunel/apps](tunel/apps) and although it is under development, it looks something like this:

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
You can currently list available apps found on these paths as follows:

.. code-block:: console

    $ tunel list-apps
    Name                 Launcher
    slurm/socket/jupyter slurm
    slurm/port/jupyter   slurm
   

If you need to use a socket (e.g., your cluster doesn't support ports) you can try:


.. code-block:: console

    $ tunel run-app waffles slurm/socket/jupyter


This will start the job, show you two options for ssh commands to connect when the notebook is ready (e.g., when the output
shows up with the token) and then you can copy paste that into a separate terminal to start the tunnel.
This might be possible to do on your behalf, but I like the user having control of when to start / stop it
so this is the current design. It will ask you for your password, and if you don't want to do that,
try adding your rsa keys to the authorized_keys file in your ~/.ssh directory on your cluster (thanks to [@becker33](https://github.com/becker33) for this tip)!
I just created an account on OSG so I should be able to work on the port connection use case soon!

app arguments
^^^^^^^^^^^^^

Apps can be customized with arguments. For example, the `slurm/socket/jupyter-singularity` app can run a jupyter notebook
or a jupyterlab instance, and to do that, you can see the argument defined in the app.yaml:

TODO

```yaml
```


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
