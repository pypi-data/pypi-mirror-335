from typing import Any

from .agent_inference import AgentInference


class Agents:
    def __init__(self, client: Any) -> None:
        self.agent = AgentInference(client)
