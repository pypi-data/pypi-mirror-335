Contributing and Development
============================

Thank you for considering to contribute to palaestrAI's development! We
appreciate bug reports and patches. palaestrAI is developed on
`Gitlab <https://gitlab.com/arl2/palaestrai>`_. There, you can access all
developer resources, such as the issue tracker and the source code.

Filing Bugs
-----------

Issues can be reported against our
`issue tracker <https://gitlab.com/arl2/palaestrai/-/issues>`_. We have a
number of pre-defined templates that help you to collect necessary information
for us to track and fix the bug. Please try to provide as much information as
possible:

* A concise description of the bug: what did you intend to do, what happened
  instead?
* The error message, if there is any.
* The command line parameters, runtime configuration, and
  experiment run file (if used)
* Your version of Python you are using, and the version of all modules
  (``pip freeze`` gives you that).

In order to gather as many information as possible, you can also run the
``palaestrai`` executable with ``-vv`` to produce debugging output. Please
be aware that this will probably lead to a lot of text, so redirecting the
output to a file is advised::

    palaestrai -vv experiment-start my_run_file.yml 2>&1 | tee debug.log


Getting the Sources
-------------------

To access the source code, clone the palaestrAI repository from
`<https://gitlab.com/arl2/palaestrai.git>`_. To install, run::

    pip install -e '.[dev]'

This allows to edit the source code and still run ``palaestrai``.

Work flow
---------

1. File a bug/feature/support request in the issue tracker
2. Create a merge request with a feature branch in Gitlab.
3. Provide a unit test for the bug/feature you have been working on.
4. Fix the bug/work on the feature.
5. Run black -l 79 ./src/palaestrai ./tests to auto-format the code
6. Run tox and clean up all errors.
   (Run tox -e full-docker to also run system tests using docker and
   docker-compose)
7. Request a merge. The merge will happen after a code review;
   work-in-progress code gets first merged into development

Once the current development branch has ripened enough, it is merged to master. 
The master branch must contain code that is stable. New releases are only
tagged on master branch commits.

Writing Tests
-------------

palaestrAI development is supported by three kinds of test cases:

1. unit tests in ``tests/unit``
2. system tests in ``tests/system``
3. integration tests in ``tests/integration``.

**Unit tests** use the standard Python facilities under ``test.unit``. They
are responsible for ensuing the functionality of individual components.

**System tests** are writting using the `Robot Framework
<https://robotframework.org/>`_. Integration tests usually run palaestrAI
itself, either from the CLI or by using the ``palaestrai.execute`` API entry
point. All system tests are run in parallel using `Pabot
<https://pabot.org/>`_. Because some tests rely on resource usage or timing
(e.g., signal tests), the execution of system tests is controlled through
the ``tests/system/ordering`` file.

**Integration tests** finally execute the larger palaestrAI stack, pulling
in packages such as ``palaestrai-environments`` or ``harl``. They, too, are
implemented using the Robot Framework.
