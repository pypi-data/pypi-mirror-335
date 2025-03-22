from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from palaestrai.agent import (
        SensorInformation,
        ActuatorInformation,
    )


@dataclass
class AgentUpdateResponse:
    """Responds after an agent has acted via its :class:`Muscle`

    * Sender: :class:`RolloutWorker`
    * Receiver: :class:`SimulationController`

    Parameters
    ----------
    sender_rollout_worker_id : str
        ID of the sending :class:`RolloutWorker` (this is the internal UID of
        the worker, which is generated, not the name of the :class:`Muscle`
        from the :class:`ExperimentRun` definiton).
    receiver_simulation_controller_id : str
        ID of the receiving :class:`SimulationController`
    experiment_run_id : str
        ID of the current experiment run this environment participates in
    experiment_run_instance_id : str
        ID of the ::`ExperimentRun` object instance
    experiment_run_phase : int
        Current phase number of the experiment run
    sensor_information : list of :class:`SensorInformation`
        List of sensor readings :class:`SensorInformation`
    actuator_information : list of :class:`ActuatorInformation`
        List of actuator actions via :class:`ActuatorInformation`
    walltime : datetime.datetime
        The time the message was created, default: datetime.utcnow()
    """

    sender_rollout_worker_id: str
    receiver_simulation_controller_id: str
    experiment_run_id: str
    experiment_run_instance_id: str
    experiment_run_phase: int
    sensor_information: List[SensorInformation]
    actuator_information: List[ActuatorInformation]
    walltime: datetime = field(default_factory=datetime.utcnow)

    @property
    def sender(self):
        return self.sender_rollout_worker_id

    @property
    def receiver(self):
        return self.receiver_simulation_controller_id

    @property
    def actuators(self):
        return self.actuator_information
