from __future__ import annotations
from typing import Optional, Union

from palaestrai.core.protocol import (
    EnvironmentUpdateResponse,
    SimulationControllerTerminationRequest,
)
from palaestrai.experiment import TerminationCondition, RunGovernor
from palaestrai.types import SimulationFlowControl


class EnvironmentTerminationCondition(TerminationCondition):
    """Terminates the current phase when an ::`~Environment` terminates

    This :class:`~TerminationCondition` examines updates from an
    :class:`~Environment` and checks whether the environment itself signals
    termination.
    """

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: Optional[Union[SimulationControllerTerminationRequest]],
    ) -> SimulationFlowControl:
        if not isinstance(message, SimulationControllerTerminationRequest):
            return SimulationFlowControl.CONTINUE
        return (
            SimulationFlowControl.RESET
            if message.environment_terminated
            else SimulationFlowControl.CONTINUE
        )

    def check_termination(self, message, component=None):
        """Checks for environment termination

        Parameters
        ----------
        message : Any
            Examines :class:`~EnvironmentUpdateResponse` messages for
            ::`~EnvironmentUpdateResponse.is_teminal`.
        component : Any
            unused

        Returns
        -------
        bool
            ``True`` if ``message.is_terminal``.
        """
        return isinstance(message, EnvironmentUpdateResponse) and message.done
