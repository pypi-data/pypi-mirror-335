Installation and Setup
======================

In this section we'll take a look at how to install palaestrAI as well as
creating a working database and adding shell-completion for the palaestrAI
CLI.

Installation
------------

There are two ways to install and use palaestrAI:

1. From PyPI for local usage
2. in a Docker container.

To install from **PyPI**, run::

    pip install palaestrai[full]

This will pull in everything you will most certainly need to start
your experiments.

Consequently, to use the **Docker** container, the command is equally simple::

    docker pull palaestrai/palaestrai:latest


As mentioned in the about section, palaestrAI is the core framework of a
whole ecosystem. So ``palaestrai[full]`` also installs *hARL* to gain
access to implementations of several deep reinforcement learning algorithms
and interfaces, *palaestrai-environments* for a number of supported environments
to play around with, and *arsenAI* for sound design of experiments. The
``palaestrai[full]`` also pulls in
`MIDAS <https://midas-mosaik.gitlab.io/midas/>`_ for experiments in
power grids. The docker container contains all this, too.

.. note::

    The PyPI packages are meant to be used by the enduser. If you
    plan to work on the *palaestrAI* framework itself, you will need to set-up
    a development environment. For further information, please take a look
    at the :doc:`contributing` page.

.. warning::

    palaestrAI does currently not support any Windows-based machines directly.
    However, using the Windows Subsystem for Linux (WSL2) works perfectly
    well.


At this point you should have installed all necessary libraries to start working with palaestrAI.
To familiarize yourself with the *palaestrai* CLI tool run::

    palaestrai --help

This will give you an overview of everything the tool has to offer.

Adding Shell Completion
-----------------------

``palaestrai`` comes with the convenience of shell completion for *bash*,
*Zsh*, and *fish*. They are installed in ``/etc/bash_completion.d``,
``/etc/zsh_completion.d`` and ``/etc/fish_completion.d`` respectively.
The ``/etc`` directory is relative to your installtion root, so if you
install palaestrAI in your *virtualenv* directory ``~/palaestrai/venv``,
then the completion files will be installed in
``~/palaestrai/venv/etc/{bash,zsh,fish}_completion.d``.

After installing the files, you'll have to source the appropriate file to
your shell script (``~/.bashrc``, ``~/.zshrc`` or ``~/.fishrc``) in order
to enable shell completion. An example for the *Zsh* shell would be::
    
    echo '. /etc/zsh_completion.d/palaestrai_completion.zsh' >> ~/.zshrc
 

Creating a Database
-------------------

In order to work with palaestrAI and save results from our experiment
runs, we need to supply a database. Before we create a database though, we
should take a step back and look at how palaestrAI sets its behavior.

palaestrAI utilizes a *Runtime Configuration* to determine its runtime
behavior, including the creation of our database. At this point we are using
a default configuration provided by *palaestrAI*. To take a look
at the default configuration run::

    palaestrai runtime-config-show-default

Notice the ``store_uri`` parameter, it configures the access to a database.
The runtime configuration is controlled using a separate configuration
file that palaestrAI will try to look up at specific locations.
If no configuration file is found, the framework will resort to the default
configuration. If you want to adjust the runtime configuration to your
needs, you'll have to place your configuration file in one of these locations:

1. ``/etc/xdg/palaestrai/runtime-conf.yaml``
2. ``$HOME/.config/palaestrai/runtime-conf.yaml``
3. ``$PWD/palaestrai-runtime.conf.yaml``
4. ``$PWD/runtime.conf.yaml``

.. note::

    The search path for the runtime configuration file is printed at the
    top of ``palaestrai runtime-config-show-default``.

You can have several runtime configuration files; each subsequently loaded
overwrites values in a cascading manner. The built-in default configuration
is always present. Then, settings in the system-wide runtime configuration
file (1) overwrite the default settings; then the files 2–4 are loaded (if
found), and finally, the runtime configuration file given by the ``-c`` flag
is loaded. It is entirely possible to have a runtime configuration file that
consists only of, e.g., the ``store_uri``: In this case, all other runtime
configuration parameters (such as logging) are taken from the built-in
defaults.

For ease of use let's dump the default-configuration to one of these
locations to modify it ourselves::

    mkdir -p $HOME/.config/palaestrai
    palaestrai runtime-config-show-default \
        > $HOME/.config/palaestrai/runtime-conf.yaml
 
As an simple example you could try to change the ``store_uri`` parameter to
rename the database file, i.e. from ``sqlite:///palaestrai.db`` to
``sqlite:///experiments.db``. Check whether your custom configuration is in
place::

    palaestrai runtime-config-show-effective

If you placed the configuration file in the right location you'll notice
that palaestrAI now utilizes your settings.

Please refer to the :doc:`runtime-config` documentation on how to further
adjust the configuration to your needs. For instance, palaestrAI
also allows the use of the more performant *PostgreSQL* database.
Familiarize yourself with the runtime configuration; there is a lot to
tinker with.

Now, after this detour lets finally create a database.
Fortunately, our palaestrai CLI tool offers a simple command to generate
such a database::

    palaestrai database-create

If you're using the default runtime configuration, you'll notice a new file
called ``palaestrai.db`` in the current directory.

Start Experimenting
-------------------

palaestrAI is set up now: head over to the :doc:`Tutorials <tutorials>`
to get  started!
