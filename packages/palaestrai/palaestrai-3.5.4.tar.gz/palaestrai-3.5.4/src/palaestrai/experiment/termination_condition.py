from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

from abc import ABC
from palaestrai.types import SimulationFlowControl

if TYPE_CHECKING:
    import palaestrai.environment
    from palaestrai.agent import Brain
    from palaestrai.experiment import RunGovernor
    from palaestrai.environment import Environment
    from palaestrai.core.protocol import SimulationControllerTerminationRequest


class TerminationCondition(ABC):
    """Control execution flow of simulations.

    Termination conditions control the flow of the simulation execution. For
    every ::`palaestrai.envrionment.Environment` update
    and every ::`palaestrai.agent.Brain` update,
    the configured termination conditions are queried.
    They then return a flow control indicator (::`SimulationFlowControl`).

    This base class offers default implementations for two situations:

    * ::`TerminationCondition.brain_flow_control`
      is called after an agent's ::`Brain` has received a ::`Muscle` update
      and had time to think about it.
    * ::`TerminationCondition.environment_flow_control`
      is called after an environment update.

    The ::`SimulationFlowControl` enum defines a number of constants. They are
    ordered, i.e., ::`SimulationFlowControl.CONTINUE` has the lowest priority,
    whereas ::`SimulationFlowControl.STOP` has the highest. The indicator
    with the highest priority wins overall, i.e., if one agent indicates that
    the simulation should stop, then it will terminate the current experiment
    run phase.
    """

    def brain_flow_control(self, brain: Brain) -> SimulationFlowControl:
        """Allows a learning process to control the simulation flow.

        A learner can control the simulation, e.g., by indicating that the
        simulation should be reset or can end when it has become good enough.
        Descendant classes can reimplement this method. They will receive
        access to the respective agent's ::`Brain`, which contains all the
        necessary information (e.g., its memory, training success, etc.)

        Returns
        -------
        ::`SimulationFlowControl` :
            An indicator for simulation control: The flow control indicator
            with the highest priority (i.e., highest value number in the
            enum) wins.
        """
        return SimulationFlowControl.CONTINUE

    def environment_flow_control(
        self, environment: palaestrai.environment.Environment
    ) -> SimulationFlowControl:
        """Allows an environment to control the simulation flow.

        The logic is the same as for ::`.brain_flow_control`, except that an
        environment is now checked.
        The default implementation is to reset the run when the environment is
        done (::`palaestrai.environment.Environment.done`).
        """
        return (
            SimulationFlowControl.RESTART
            if environment.done
            else SimulationFlowControl.CONTINUE
        )

    def phase_flow_control(
        self,
        run_governor: RunGovernor,
        message: Optional[Union[SimulationControllerTerminationRequest]],
    ) -> SimulationFlowControl:
        """Allows overall control of a simulation phase via the ::`RunGovernor`

        The logic is similar to the of ::`.brain_flow_control`, with the
        exception that this function is called in the ::`RunGovernor`.
        """
        return SimulationFlowControl.CONTINUE

    def check_termination(self, message, component=None):
        return False
