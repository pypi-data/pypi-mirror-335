PalaestrAI CLI
==============

PalaestrAI offers a number of useful CLI-Commands, in this section we'll take a look
at what the CLI has to offer.

Commands
--------

experiment-start
~~~~~~~~~~~~~~~~
Starts one or more experiments from a file or directory.
Provide it with a path to a file or directory. Directories are expanded and recursevly searched
for experiment run files.

Example::

    palaestrai experiment-start tests/fixtures/dummy_run.yml

database-create
~~~~~~~~~~~~~~~
Creates the store database that is required for running experiments.
This needs a valid runtime configuration file. Note that we offer a default configuration that is utilized
by simply running the command.

Example::

    palaestrai database-create

database-migrate
~~~~~~~~~~~~~~~~

runtime-config-show-default
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shows the default runtime config and the search paths.

Example::

    palaestrai runtime-config-show-default

runtime-config-show-effective
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shows the currently effective runtime config.

Example::

    palaestrai runtime-config-show-effective

experiment-check-syntax
~~~~~~~~~~~~~~~~~~~~~~~
Checks provided experiment run files for syntactic correctness. 
You can call this command with both files and directories.
Directories will be recursively searched for experiment files.

Example::

    palaestrai experiment-check-syntax tests/fixtures/dummy_run.yml

experiment-list
~~~~~~~~~~~~~~~
This will list your run experiments.
Call it with a specific database or simply run it to use the database in your effective runtime config.

This command offers a number of useful flags::

    --format
    The command will print the output utilizing Tabulate. This library offers a number of formating
    schemes that you can use as desired. Check out the Tabulate documentary for all available format options.

    Example:
        palaestrai experiment-list --format=pipe

    --limit
    Limits the output to a number of your choice. If you just want to look-up 20 experiments you can call:
      
       palaestrai experiment-list --limit=20

    --offset
    Provide an offset to the command if you want to skip a certain number of experiments. If you want to skip the first 
    10 experiments call:

        palaestrai experiment-list --offset=10

    --database
    If you want to list the experiments from a specific database file use this command.
    Make sure to provide the proper database prefix, e.g. 'sqlite:///'. For example:

        palaestrai experiment-list --database=sqlite:///experiments_january.db

    --csv
    Depending on the number of experiments you might end up with a huge result set. If instead of printing the results through the CLI
    you want to write the output to a csv-file use this command. For example:

        palaestrai experiment-list --csv=experiments_january.csv
