.. _getting_started-developer-guide:

===============
Developer Guide
===============

This developer guide includes more complex interactions like contributing
apps and launchers. If you haven't read :ref:`getting_started-installation`
you should do that first.

Tunel Apps
==========

When you write an app, it comes down to putting an ``app.yaml`` under some nested
subfolder of the tunel app folders (or a custom one that you've created and adding
to your tunel settings under ``apps_dirs``.  The yaml should have basic metadata
along with its needs and arguments the user can provide. We require detail (e.g., descriptions)
to ensure that rendering the app into documentation is useful for users.
A basic application might look like the following:

.. code-block:: yaml

    launcher: slurm
    script: jupyter.sbatch
    description: A jupyter notebook (or lab) intended to be run in a Singularity container.
    args:
     - name: jupyterlab
       description:  Try running jupyterlab instead (e,g. set to true to enable) 
     - name: workdir
       description: Working directory for the notebook
     - name: modules
       description: comma separated list of modules to load
       split: ","
    needs:
      socket: true
  
Note that all of the fields (except for needs) are required. Args are not required but recommended,
described next.

Launchers
---------

Launchers include:


 - **singularity** run a singularity container on the server directly.
 - **docker** run a docker container on the server directly (experimental support for podman)
 - **slurm**: submit jobs (or applications) via SLURM, either a job or a service on a node to forward back.
 - **condor**: submit jobs (or apps) to an HTCondor cluster.

And currently it's up to you to handle your application script logic. E.g., if you are using the singularity launcher
and calling singularity in your script, you should check that it's installed and write a clear error message if not.
The exception is docker, which we have a template variable to check for, e.g.,:

.. code-block:: console

    {% if docker %}
    # do docker stuff here
    {% else %}
    # do something else
    {% endif %}


Needs
-----

Each app can specify a set of boolean needs to indicate to the launcher how t do setup.
A specification might look like the following in your ``app.yaml``:

.. code-block:: console

    needs:
      xserver: true
      socket: false

If something is false, it's not required to incldue.

socket
^^^^^^

If the app uses a socket, any existing *.sock files in the app directory on the remote will be cleaned up.
In your application primary running script, you can easily create the socket relative to the script directory,
and a helper include will ensure that we define the `SOCKET` environment variable and clean up any previous one.

.. code-block:: console

    SOCKET_DIR="{{ scriptdir }}"
    mkdir -p ${SOCKET_DIR}

    echo "Socket directory is ${SOCKET_DIR}"

    # Remove socket if exists
    {% include "bash/socket/set-socket.sh" %}

It's helper to look at other application scripts.


xserver
^^^^^^^

An xserver doesn't use typical ssh tunnel strategies like using a socket, but instead forwards with `-X`.
This means we have support primarily for Singularity (running the container on the head node) and
slurm (the same from a job node).


Args
----

Args ("args") should be a list of arguments, each of which contains a name and description,
 that can be rendered in your template and user documentation. The field "split"
 is not required, but if provided, means that any user provided argument will be split by that
 character. As examples of the above:

.. code-block:: console

    $ tunel run-app osg slurm/socket/jupyter --workdir=/usr/username/workdir --modules=python/3.7,py-tensorflow

Commands
--------

Commands (in the app.yaml, ``commands:`` might be wanted if, for example, your app generates a login credential
that you want to cat to the terminal for the user. It's recommended to design your app to have an artificial home
in the ``$SOCKET_DIR`` and then to designate it as home (e.g., ``--home`` with singularity. Currently, tunel supports
a post command (for Singularity only) that might look like this:

.. code-block:: yaml

    commands:
      post: cat $socket_dir/home/.config/code-server/config.yaml

The above will substitute ``$socket_dir`` with the socket directory on the cluster,
and you will have made the ``$socket_dir/home`` folder and designated it as ``--home``
to singularity. See the singularity/socket/code-server app for an example.


Includes
--------

Since there is often shared logic between apps, we have a shared templates
folder in which you can write snippets that intend to be shared. As an example,
it's fairly common with Singularity containers to want to check for a cache directory
being set, and if it's not set, set it somewhere with a lot of space (e.g., a temporary
filesystem). The snippet in bash might look like this:

.. code-block:: console

    if [ -z ${SINGULARITY_CACHEDIR+x} ]; then 
        export SINGULARITY_CACHEDIR=/tmp
    fi

And then within your templates for a script or sbatch script, instead of needing
to write that out many times (and update each one) you can include the template:

.. code-block:: console

    # Include Singularity cachedir if not set
    {% include "bash/singularity-cache-tmp.sh" %}

Note that this templates directory is at ``tunel/templates`` and should be organized
logically (e.g., by language or other relevant context).


Template Variables
------------------

If you write a job file or template, in addition to arguments that the user might
provide on the command line (and you should always set a default for) the following
variables are always available:

.. list-table:: Template Variables
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - args
     - Dictionary of arguments that a user might provide from the command line (e.g., ``{{ args.cpus }}``.
     - {}
   * - paths
     - List of paths derived from the launcher config in settings, plus any from the app.needs.path section of an app.yaml
     - []
   * - jobslug
     - The full job name with path separators replaced with single dashes. E.g., ``{{ jobslug }}`` renders to ``htcondor-job``
     - defaults to the job name slugified
   * - jobname
     - The job name, automatically assigned
     - defaults to the job name
   * - port
     - ssh remote port
     - defaults to the default in your settings.yaml
   * - scriptdir
     - the remote assets directory plus the app name
     - As an example, ``${HOME}/tunel/htcondor/job``
   * - socket
     - fullpath to a socket file (.sock) in case the job needs one
     - As an example, ``${HOME}/tunel/htcondor/job/htcondor-job.sock``     
   * - script
     - fullpath to a main job script ("script" in the app.yaml) post-render
     - As an example, ``${HOME}/tunel/slurm/jupyter/jupyter.sbatch``
   * - script_basename
     - The script basename
     - As an example, ``jupyter.sbatch``
   * - log_output
     - log output file (*.out) in the scriptdir
     - As an example, ``jupyter.sbatch.out``
   * - log_error
     - log error file (*.err) in the scriptdir
     - As an example, ``jupyter.sbatch.err``
   * - log_file
     - single logging file (if needed) in the scriptdir
     - As an example, ``jupyter.sbatch.log``
   * - workdir
     - If ``tunel_remote_work`` is defined in settings, this variable first, overridden by --workdir on the command line.
     - As an example, ``/usr/workdir/username/``
     
Finally, you can use the set of included templates under ``tunel/templates`` to include common functionality like
sourcing the user bash profile. You can also add any template file (or subfolder) in your app directory
and it can be discovered and included. E.g., ``templates/run_docker.sh`` can be included like ``{% include "templates/run_docker.sh" %}.

Documentation
-------------

Tunel has a special command to generate docs, and they are written to ``apps`` in the
present working directory that gets built into "apps" of the website. To generate:

.. code-block:: console

    $ tunel docgen apps/_library/
    Generating documentation markdown for htcondor/job
    Generating documentation markdown for slurm/socket/singularity-jupyter
    Generating documentation markdown for slurm/socket/jupyter
    Generating documentation markdown for slurm/port/jupyter
    Generating documentation markdown for singularity/socket/jupyter


    
