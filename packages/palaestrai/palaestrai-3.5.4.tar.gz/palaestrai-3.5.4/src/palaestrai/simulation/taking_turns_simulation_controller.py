from __future__ import annotations

import asyncio
import logging
import uuid
from asyncio import Future
from collections import defaultdict
from itertools import product, chain
from typing import (
    TYPE_CHECKING,
    Any,
    Sequence,
    Dict,
    List,
    Set,
    Union,
    Tuple,
    Optional,
)

from palaestrai.core import BasicState
from .simulation_controller import SimulationController

# from palaestrai.util.exception import SimulationSetupError
from palaestrai.types import SimTime
from palaestrai.util.dynaloader import load_with_params

if TYPE_CHECKING:
    from palaestrai.types import Mode
    from palaestrai.experiment import TerminationCondition
    from palaestrai.agent import (
        SensorInformation,
        ActuatorInformation,
        RewardInformation,
    )

LOG = logging.getLogger(__name__)


class TakingTurnsSimulationController(SimulationController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def simulate(self):
        """Main simulation task

        This method is usually scheduled as a task at the end of the simulation
        setup phase. It can be overwritten by descendant classes to excert
        complete control over the simulation.
        """
        agents = list(self._agents.values())  # Needed to preserve order
        ai = 0  # Index of current agent
        env_terminates = False

        while self.is_running:
            # With the index ai, we iterate over agents in the order in which
            # they were loaded, which, in turn, is given by the order in
            # which comes from the ExperimentRun object.
            # The index ai wraps (see the end of the loop).
            # Python's dict is guaranteed to remember the order in which items
            # were added to it (since Python version 3.7).

            agent = agents[ai]
            response = (await self.act([agent]))[0]

            # Check for a termination signal from the agent,
            # then apply the setpoints to the environments, and
            # advance state:

            interrupt_flow, terminations = self.interrupt_flow([response])
            LOG.debug(
                "%s checks whether %s interrupts the flow: "
                "interrupt_flow: %s, terminations: %s",
                self,
                response,
                interrupt_flow,
                terminations,
            )
            if interrupt_flow:
                LOG.info(
                    "Action from rollout worker %s triggers "
                    "termination conditions(s) %s, "
                    "stopping this episode.",
                    response.sender,
                    [tc for tc, triggers in terminations.items() if triggers],
                )
                self._state = BasicState.STOPPING
                break  # Break from agent iteration loop

            # Get environments states
            env_updates = await self.step([agent], response.actuators)

            # Does any of the environments lead to termination of the
            # current phase?
            interrupt_flow, terminations = self.interrupt_flow(env_updates)
            if interrupt_flow:
                LOG.info(
                    "Environment(s) %s end(s) the simulation via "
                    "termination condition(s) %s.",
                    ", ".join(
                        [e.environment_name for e in env_updates if e.done]
                    ),
                    [tc for tc, triggers in terminations.items() if triggers],
                )
                self._state = BasicState.STOPPING

            ai = (ai + 1) % len(agents)

            if interrupt_flow:
                env_terminates = interrupt_flow
                break  # Break from agent iteration loop
        LOG.debug(
            "The simulation has ended, updating agents one last time.",
        )
        # Notify agents of our terminal state. We can potentially parallelize
        # here, as order is no longer important: Each agent gets the same
        # final state, no actions are applied anymore.
        _ = await self.act(agents, done=True)
        self.flow_control(environment_done=env_terminates)
