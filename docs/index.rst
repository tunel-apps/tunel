.. _manual-main:

=====
Tunel
=====

.. image:: https://img.shields.io/github/stars/tunel-apps/tunel?style=social
    :alt: GitHub stars
    :target: https://github.com/tunel-apps/tunel/stargazers

Developer tools for HPC. Because we can't have cloud but we want nice things too.

Tunel is named for what it does. "Tunel" is an elegant derivation of "tunnel" and will do exactly that - 
create a tunel between your local workstation and an HPC cluster. Tunel tries to abstract away some 
of the complexity of launching interfaces that feel a bit more modern.
In its simplest form this means:

 1. Installing tunel locally and discovering what is available on your cluster
 2. Running a local server (or via the command line) selecting and configuring an application to run.
 3. Launching it via a ssh tunnel to your cluster resource
 4. Getting back an address to open up and start working.

The library contains a collection of apps that are ready to go, and you can also use one of our
templates to create your own! Head over to see `currently provided applications <_static/apps/>`_
or to see the code, head over to the `repository <https://github.com/tunel-apps/tunel/>`_.


.. _main-getting-started:

--------------------------
Getting started with Tunel
--------------------------

Tunel can be installed from pypi or directly from the repository. See :ref:`getting_started-installation` for
installation, and then the :ref:`getting-started` section for using the client.

.. _main-support:

-------
Support
-------

* For **bugs and feature requests**, please use the `issue tracker <https://github.com/tunel-apps/tunel/issues>`_.
* For **contributions**, visit Caliper on `Github <https://github.com/tunel-apps/tunel>`_.

---------
Resources
---------

`GitHub Repository <https://github.com/tunel-apps/tunel>`_
    The code on GitHub.
`Tunel Apps <_static/apps/>`_
    Current applications and launchers supported by tunel.


.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 3

   getting_started/index
   getting_started/user-guide
   getting_started/developer-guide

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 2

    api_reference/modules
