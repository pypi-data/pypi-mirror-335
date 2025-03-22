import unittest
from unittest.mock import MagicMock, AsyncMock, call

from palaestrai.types.mode import Mode
from palaestrai.agent import ActuatorInformation
from palaestrai.core.protocol import AgentUpdateResponse
from palaestrai.types import Discrete, SimulationFlowControl

from palaestrai.simulation.vanilla_sim_controller import VanillaSimController


class VanillaSimulationControllerTest(unittest.IsolatedAsyncioTestCase):
    async def test_advance(self):
        self.sc = VanillaSimController(
            agent_conductor_ids=["AC-1", "AC-2"],
            environment_conductor_ids=["EC-1", "EC-2"],
            agents={},
            mode=Mode.TEST,  # Ha-ha.
            termination_conditions=[{}],
        )
        actuator_infos = [
            ActuatorInformation(uid="AI-1.1", space=Discrete(4711), value=815),
            ActuatorInformation(uid="AI-1.2", space=Discrete(4711), value=815),
            ActuatorInformation(uid="AI-2.1", space=Discrete(4711), value=816),
            ActuatorInformation(uid="AI-2.2", space=Discrete(4711), value=816),
        ]
        self.sc._agents = {
            "AC-1.RW-1": MagicMock(
                uid="AC-1.RW-1", actuators=actuator_infos[:2]
            ),
            "AC-2.RW-2": MagicMock(
                uid="AC-2.RW-2", actuators=actuator_infos[2:]
            ),
        }
        self.sc.act = AsyncMock(
            return_value=[
                AgentUpdateResponse(
                    sender_rollout_worker_id="RW-1",
                    receiver_simulation_controller_id="SC-1",
                    experiment_run_id="run away",
                    experiment_run_phase=42,
                    experiment_run_instance_id="Insta-1234",
                    sensor_information=[],
                    actuator_information=actuator_infos[:2],
                ),
                AgentUpdateResponse(
                    sender_rollout_worker_id="RW-2",
                    receiver_simulation_controller_id="SC-1",
                    experiment_run_id="run away",
                    experiment_run_phase=42,
                    experiment_run_instance_id="Insta-1234",
                    sensor_information=[],
                    actuator_information=actuator_infos[2:],
                ),
            ]
        )
        self.sc.step = AsyncMock()
        self.sc.interrupt_flow = MagicMock(
            side_effect=[
                (
                    False,
                    {},
                ),
                (
                    False,
                    {},
                ),
                (
                    True,
                    {},
                ),
            ]
        )
        agent_flow_control, env_flow_control = await self.sc.advance()
        self.assertEqual(agent_flow_control, SimulationFlowControl.CONTINUE)
        self.assertEqual(env_flow_control, SimulationFlowControl.CONTINUE)
        agent_flow_control, env_flow_control = await self.sc.advance()
        self.assertEqual(agent_flow_control, SimulationFlowControl.RESET)
        self.assertEqual(env_flow_control, SimulationFlowControl.CONTINUE)
        self.sc.step.assert_awaited_with(self.sc.agents, actuator_infos)


if __name__ == "__main__":
    unittest.main()
