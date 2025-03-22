from __future__ import annotations
from typing import Tuple

import logging
import itertools

from palaestrai.types import SimulationFlowControl
from .simulation_controller import SimulationController

LOG = logging.getLogger(__name__)


class VanillaSimController(SimulationController):
    """Scatter-gather simulation controller for agents

    This simulation controller implements an execution strategy in which agents
    act in parallel.
    """

    async def advance(
        self,
    ) -> Tuple[SimulationFlowControl, SimulationFlowControl]:
        rsp = await self.act(self.agents)
        agents_interrupt, _ = self.interrupt_flow(rsp)
        if agents_interrupt:
            return SimulationFlowControl.RESET, SimulationFlowControl.CONTINUE
        rsp = await self.step(
            self.agents,
            [
                a
                for a in itertools.chain.from_iterable(
                    [r.actuators for r in rsp]
                )
            ],
        )
        environments_interrupt, _ = self.interrupt_flow(rsp)
        if environments_interrupt:
            return SimulationFlowControl.CONTINUE, SimulationFlowControl.RESET
        return SimulationFlowControl.CONTINUE, SimulationFlowControl.CONTINUE
