from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

import logging

from .termination_condition import TerminationCondition
from ..core.protocol import SimulationControllerTerminationRequest
from ..types import SimulationFlowControl

if TYPE_CHECKING:
    from palaestrai.experiment import RunGovernor

LOG = logging.getLogger(__name__)


class MaxEpisodesTerminationCondition(TerminationCondition):
    """Checks whether a maximum number of episodes has been exceeded."""

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: Optional[Union[SimulationControllerTerminationRequest]],
    ) -> SimulationFlowControl:
        if not isinstance(message, SimulationControllerTerminationRequest):
            return SimulationFlowControl.CONTINUE
        if run_governor.experiment_run is None:
            LOG.warning(
                "MaxEpisodesTerminationCondition cannot control flow: "
                "Run governor has no experiment run object!"
            )
            return SimulationFlowControl.CONTINUE
        max_episodes = run_governor.experiment_run.get_episodes(
            run_governor.current_phase
        )

        # If all SCs have reached the max number of episodes, indicate end of
        # the phase:

        if all(
            x >= max_episodes
            for x in run_governor.current_episode_counts.values()
        ):
            return SimulationFlowControl.STOP_PHASE

        # If only the current one, indicate shutdown of the current simulation
        # controller:

        sc_uid = message.sender
        if run_governor.current_episode_counts[sc_uid] >= max_episodes:
            return SimulationFlowControl.STOP_SIMULATION
        return SimulationFlowControl.CONTINUE
