palaestrai.agent
================

Algorithms: Agent, Brain, and Muscle
------------------------------------

Agent
~~~~~

An agent is a container for :class:`~Brain` (trainer), :class:`Muscle`(s)
(worker), and :class:`Objective` (objective reward defintion of an agent).

.. autoclass:: palaestrai.agent.Agent
   :members:
   :show-inheritance:

agent.State
~~~~~~~~~~~

Denominates the stages of an agent's lifecycle.

.. automodule:: palaestrai.agent.state
   :members:

Brain
~~~~~

Each agent has a brain, which stores experiences gather by its
:class:`~Muscle`\s (workers) and learns from them.

.. autoclass:: palaestrai.agent.Brain
    :members:

Muscle
~~~~~~

Muscles are the worker objects of an agent. They act within an
:class:`~Environment`, performing policy inference.

.. autoclass:: palaestrai.agent.Muscle
    :members:

AgentConductor
~~~~~~~~~~~~~~

An agent conductor is the guardian of all agent objects' lifecycle. Each
agent (one brain, at least one muscle) is governed by an
:class:`~AgentConductor`. This conductor supervises subprocesses, establishes
communication channels, and performs watchdog duties. The
:class:`~AgentConductor` is not part of the algorithmic definition of a
learning agent, but exists purely for software engineering reasons.

.. autoclass:: palaestrai.agent.AgentConductor
   :members:

State, Action, and Rewards
--------------------------

SensorInformation
~~~~~~~~~~~~~~~~~

Sensor data an agent receives. In simple cases, a list of
:class:`SensorInformation` objects describe the full state of the
environment. More complex, realistic cases include the agent not receiving
the full state, or even a modified state. Each :class:`SensorInformation`
object describes one reading (data point) of one sensor of an agent.

.. automodule:: palaestrai.agent.SensorInformation
   :members:

ActuatorInforation
~~~~~~~~~~~~~~~~~~

Stores a set point for one actuator of an agent.

.. autoclass:: palaestrai.agent.ActuatorInformation
   :members:

RewardInformation
~~~~~~~~~~~~~~~~~

Environments issue rewards: A reward describes the current performance of
an environment with regards to its current state.

.. autoclass:: palaestrai.agent.RewardInformation
   :members:
   :undoc-members:
   :show-inheritance:

Objective
~~~~~~~~~

Describes the agents success at reaching its internal objective. The
:class:`Objective` object encapsules a function that rates the agent's
current performance, given state data, actions, and rewards.

.. autoclass:: palaestrai.agent.Objective
   :members:
   :show-inheritance:

Example (Dummy) Implementations
-------------------------------

DummyBrain
~~~~~~~~~~

.. autoclass:: palaestrai.agent.DummyBrain
   :members:
   :show-inheritance:

DummyMuscle
~~~~~~~~~~~

.. autoclass:: palaestrai.agent.DummyMuscle
   :members:
   :show-inheritance:

DummyObjective
~~~~~~~~~~~~~~

.. autoclass:: palaestrai.agent.DummyObjective
   :members:
   :show-inheritance:

