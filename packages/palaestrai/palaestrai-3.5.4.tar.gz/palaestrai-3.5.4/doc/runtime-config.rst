Runtime Configuration
=====================

Introduction
------------
The Runtime Configuration is responsible for setting up operational options of the PalaestrAI framework.
By providing our own configuration it allows to set several functionalities/options of the run,
like the type of store to be used, which ports to be used and the logging level of different classes. 

..  note:: The configuration of the RuntimeConfig is seperate from the configuration of an experiment. 


Configuration
-------------
The configuration of the RuntimeConfig goes through several phases.
First it loads default values which are built into the framework.
Then it looks up the standard search paths and then, subsequently, loads any stream, file path or dictionary that is supplied by the user.
Note that the RuntimeConfig *always* runs through these phases and each subsequent load updates the config accordingly.
That means that the user provided values have preference over the previous configurations.

The seperate runtime configuration file is written in the *YAML* format.
For an easy example please refer to an existing runtime configuration, for example:
``palaestrai/tests/fixtures/palaestrai-runtime-debug-conf.yaml``

Lets take a look at all available config file options.
All examples were taking from the *default configuration*. 
(Note: you can display the default configuration at any time by running:
``palaestrai runtime-config-show-default``
To display the *currently effective* runtime configuration run:
``palaestrai runtime-config-show-effective``)

- **store_uri**
    Set the URI to the backend database. It is using SQLalchemy so you need to make sure to 
    provide a *Database URL* that is supported by this library, currently supported url-schemes are
    ``postgresql://`` and ``sqlite://`` 
    Example: ``sqlite:///palaestrai.db`` (*str* value)
    Refer to the SQLalchemy documentation for further information on the url-schemes (https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls)

- **executor_bus_port**
    Sets the port on which the executor listens.
    *Note*: the *executor* is responsible for receiving new experiment runs and distributing them to existing
    *RunGovernor* instances.
    Example: ``4242`` (int value)

- **logger_port**
    Sets the port on which the internal log server listens.
    Example: ``4243`` (int value)

- **public_bind**
    A *boolean* flag which indicates whether to bind to all public IP addresses or to localhost.
    Setting this to ``True`` binds the executor and all other message buses to all public IP addresses.
    Setting this to ``False`` the buses will bind to the *localhost* only. 

- **major_domo_client_timeout**
    Sets the timeout in *seconds* for the *MajorDomoClient*.
    *Note*: the MajorDomoClient is an implementation of the ZeroMQ MDP/Worker spec, responsible as the initiator of tasks and
    messaging workers with messages.
    Example: ``300_000`` (int value)

- **major_domo_client_retries**
    Sets the number of retries the *MajorDomoClient* will try.
    Example: ``3`` (int value)

- **profile**
    A *boolean* flag which decides whether to enable profiling or not.
    Example: ``False``

- **logging**
    Configures all subsystem loggers. These are directly fed to *Python's logging facilities*.
    Please refer to the official Python documentary for further information: (https://docs.python.org/3/library/logging.config.html#logging-config-dictschemia)


Search Paths
------------
As mentioned in the introduction the configuration runs through seperate phases in configuring the RuntimeConfig, each updating the config and
taking preference to the former.
After loading the built-in default values the RuntimeConfig searches through its standard search paths.

These search paths are generated at runtime. 
To check which paths your RuntimeConfig instance is looking up run the following command:

``palaestrai runtime-config-show-default`` 

To modify the beavior of the runtime search-path lookup, refer to the ``CONFIG_FILE_PATHS`` list in the
*RunetimeConfig class*.


RuntimeConfig as an API
-----------------------
To further config the RuntimeConfig inside your code palaestrAI provides an
easy-to-use API.

- **Load a configuration from an external source**
    ``RuntimeConfig().load(stream_path_or_dict)``
    The ``load()`` method understands the following argument types:
    - **str**:    Path to a YAML configuration file
    - **TextIO**: A serialized YAML configuration in text form
    - **dict**:   A dictionary containing config key/value pairs to be
    applied directly
    Because the RuntimeConfig subsequently updates the configuration from
    the default values it is possible to not only provide a complete
    configuration but also just a number of options we as the user want to
    change. Running this with invalid input will throw an error and
    fallback to the existing configuration.
- **Reset the Runtime configuration to an empty state**
    ``RuntimeConfig().reset()``
