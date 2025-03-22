.. image:: _static/PalaestrAI_Logo_final.svg

palaestrAI: A Training Ground for Autonomous Agents
===================================================

About
-----

palaestrAI is a distributed framework to train and test all kinds of
autonomous agents. It provides interfaces to any environment, be it
OpenAI Gym or co-simulation environments via mosaik. palaestrAI can
train and test any kind of autonomous agent in these environments:
From Deep Reinforcement Learning (DRL) algorithms over model-based to
simple rule-based agents, all can train and test with or against
each other in a shared environment.

In short, palaestrAI can...

* ...train and test one or more agent of any algorithm
* ...place the agents on one or several environments at once,
  depending on the agents' algorithm
* ...provides facilities to define and reproducibly run experiments

palaestrAI is the core framework of a whole ecosystem:

* hARL provides implementations of several DRL algorithms and
  interfaces to existing DRL libraries.
* arsenAI provides all facilities needed for proper design
  of experiments.
* palaestrai-mosaik is a interface to the mosaik co-simulation
  software
* palaestrai-environments provides a number of simple,
  easy to use environments for playing with palaestrAI

Use Cases
---------

palaestrAI is the framework for the Adversarial Resilience Learning
(ARL) reference implementation. The ARL core concept consists of two
agents, attacker and defender agents, working an a common model of a
cyber-phyiscal system (CPS). The attacker's goal is to de-stabilize the CPS,
whereas the defender works to keep the system in a stable and operational
state. Both agents do not perceive their opponent's actions directly, but only
the state of the CPS itself. This imples that none of the agents knows whether
anything they perceive through their sensors is the result of the dynamics of
the CPS itself or of another agent's action.  Also, none of the agents has an
internal model of the CPS. Attacker and defender alike have to explore the CPS
given their sensors and actuators independently and adapt to it. ARL is, in
that sense, suitable to a reinforcement learning approach.  Combined with the
fact the both agents do not simply learn the CPS, but also its respective
opponent, ARL implements system-of-systems deep reinforcement learning.

.. toctree::
    installing
    quickstart
    Tutorials <tutorials>
    cli
    Experiment Scheduler <experiment-scheduler>
    Experiment Run Documents <experiment-runs>
    Access results <store>
    Runtime Configuration: Tweaking how palaestrAI Executes <runtime-config>
    Using Your Algorithms with palaestrAI <brain-muscle-api>
    Reward <reward>
    Memory <memory>
    Implementing Environments <environments>
    contributing
    Internal Architecture <architecture>
    palaestrAI API <palaestrai>

