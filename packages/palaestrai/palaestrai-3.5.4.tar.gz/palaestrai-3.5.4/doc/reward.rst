Reward and objective
=====================

Basic idea and problem
------------------------
In traditional Deep Reinforcement Learning (DRL) the reward is calculated by the environment. This can happen after each
step or as a delayed reward after a couple of steps or at the end of e.g. a game. This concept works great if you have one agent
and an environment (:class:`palaestrai.environment.environment.Environment`). The environment can link the actions taken by the agent to the next state
and could then calculate a reward. In palaestrai we have a different situation. First of all, palaestrai is designed to be used with the ARL-concept
for training agents. So we have at least two agents, which compete on the same environment. If the agents act
independently this problem could also be solved, because we would still have the actions taken by one agent and the
following state. However, if more than two agents are acting at the same time, it becomes difficult to determine which
action influenced the next state, and by how much. The calculation of the reward becomes difficult and is not very precise.
Because of that we changed the way we calculate the reward and split it in two parts.
1. The calculation of an environment reward.
2. The interpretation of the environment reward by the agent resulting in the internal reward.

Environment Reward
--------------------
The environment reward is an evaluation of the environment. It has to be implemented for each environment, sometimes it
needs a problem specific implementation as well.

.. note::
    Example:
    The environment is a planet with a limited amount of resources and living things. The reward of the environment is the combined
    life quality of all living things on this planet. The agent might be a capitalistic business human. The objective of this agent
    is to maximize his virtual monetary profits. In this case the agent would use the current state of the environment and the
    reward to calculate its internal reward. The reward could be based on the profits and only uses the environment reward to ensure
    that his/hers own existence is not in direct danger. In the ARL context, this Agent would be an attacker.
    The objective of a defender agent would focus on the environment reward and would try to maximize it to prevent decreasing life quality.
    This example should show, that an environment reward is used to calculate, e.g., the health of the environment and the objective
    of the agent is used to analyze given information to calculate the agents internal reward. The objectives of the agents can
    differ completely. In this case on agent has an economical objective the second an ecological objective.

Possible are also multiple environment rewards, for example one per agent.

Agent Objective
----------------
The agent objective is the second part of the overall reward calculation. It uses the last actions and the environment reward
and calculates an internal reward. This internal reward can be compared with the reward used traditionally. It evaluates
the actions the agent has taken based on the next environment step.
For this, the brain class calls the (:func:`palaestrai.agent.objective.Objective.internal_reward`) which takes a list of
(:class:`palaestrai.agent.reward_information`) and then has to calculate one internal reward (float).

.. Note::
    A variable for opponents is very useful. To use the example of the tank again, if Agent 1 wants to fill the tank and
    Agent 2 wants to empty it, the reward can simply be inverted. Sometimes a bigger differentiation between two opponents
    is needed.

.. warning::
    The objective is very sensible to the used environment reward. Please always check if both are compatible.

