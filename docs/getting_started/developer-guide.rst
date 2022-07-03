.. _getting_started-developer-guide:

===============
Developer Guide
===============

This developer guide includes more complex interactions like contributing
apps and launchers. If you haven't read :ref:`getting_started-installation`
you should do that first.


Tunel Apps
==========

Args
----

When you write an app, it comes down to putting an ``app.yaml`` under some nested
subfolder of the tunel app folders (or a custom one that you've created and adding
to your tunel settings under ``apps_dirs``. An app definition looks like this:

.. code-block:: yaml

    launcher: singularity
    script: jupyter.sh
    args:
     - container

Note that args should be a list of arguments that can be rendered in your template.
If you need a default, this should be provided on the level of the template.

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
