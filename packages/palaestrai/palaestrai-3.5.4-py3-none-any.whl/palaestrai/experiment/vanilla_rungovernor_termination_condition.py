from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

from .termination_condition import TerminationCondition
from .environment_termination_condition import EnvironmentTerminationCondition
from .max_episodes_termination_condition import MaxEpisodesTerminationCondition
from palaestrai.types import SimulationFlowControl

if TYPE_CHECKING:
    from palaestrai.core.protocol import SimulationControllerTerminationRequest
    from .run_governor import RunGovernor


class VanillaRunGovernorTerminationCondition(TerminationCondition):
    def __init__(self):
        self._max_episode_tc = MaxEpisodesTerminationCondition()
        self._env_tc = EnvironmentTerminationCondition()

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: Optional[Union[SimulationControllerTerminationRequest]],
    ) -> SimulationFlowControl:
        dones = [
            self._max_episode_tc.phase_flow_control(run_governor, message),
            self._env_tc.phase_flow_control(run_governor, message),
        ]
        return sorted(dones, key=lambda x: x.value)[-1]
