Access results
==============

The Store hooks into the global communication between several classes,
most notably ``environment``, ``muscle`` and ``brain``. It extracts
interesting information and saves it to a database.

Query API
---------

palaestrAI's database backend offers a simple (but growing) API for querying.
It is accessible from the ::`palaestrai.store.query` module.
The module integrates with the runtime configuration, i.e., the global
database credentials configuration is also used here.
The query API is convienient as it returns pandas or dask dataframes, which
can then be easily used in Jupyter notebooks or for plotting.

.. automodule:: palaestrai.store.query
    :noindex:

Low-Level Access
----------------

When the query API is not sufficient, the database can be accessed using the
ORM classes in ::`palaestrai.store.database_model`.
An example would be::

    import palaestrai.core
    import palaestrai.store.database_model as dbm
    import sqlalchemy.orm
    import json

    # pandapower is used by midas environments, this might differ by usecase
    import pandapower as pp
    from pandapower.plotting import simple_plot

    # Create an alchemy engine
    alchemyEngine= create_engine('postgresql+psycopg2://postgres:passwordforpalaestrai@127.0.0.1:5432/Palaestrai', pool_recycle=3600);
    # Create a session
    session_maker = sqlalchemy.orm.sessionmaker()
    session_maker.configure(bind=alchemyEngine)
    dbSession = session_maker()

    # Query experiments
    query= dbSession.query(dbm.Experiment)
    # Get the last experiment
    exps = query.order_by(dbm.Experiment.id.desc())
    exp = exps[1]
    # Get all runs
    runs = exp.experiment_runs
    run = runs[0]
    # Get all simulation runs
    sims = run.simulation_instances
    sim = sims[0]
    # Get all muscles
    muscles = sim.muscles
    muscle1 = muscles[0]
    muscle2 = muscles[1]
    # Get all muscle actions
    m1_actions = muscle1.muscle_actions
    # Get rewards from the muscle actions
    rewards = [a.reward for a in muscle1.muscle_actions]

    # Get environment conductors
    ecs = sim.environment_conductors
    # Get first ec
    ec = ecs[0]
    # Get world states
    world_states = ec.world_states


    # get the last 10 states but not the last one because its empty
    states = world_states[-10:-1]

    # for every state load the json
    # extract the external grid state
    # load the panda power net
    # extract the values and store it
    external_grids = None
    for state in states:
        world_state_json = json.loads(state.state_dump)
        s = [x for x in world_state_json if x["sensor_id"] == "Powergrid-0.Grid-0.grid_json"]
        net = pp.from_json_string(s[0]['sensor_value'])
        if external_grids is None:
            external_grids = net.res_ext_grid
        else:
            external_grids = external_grids.append(net.res_ext_grid)

    # Since the data are present in their original form,
    # all functions from the pandapower framework are applicable for data analysis,
    # for example build-in plotting functions:
    simple_plot(net)

To get a full overview of what can be done with the databse model visit
`The SQLAlchemy Documentation <https://www.sqlalchemy.org/library.html>`_.
An overview of the data-structure can be found below.

.. eralchemy::

