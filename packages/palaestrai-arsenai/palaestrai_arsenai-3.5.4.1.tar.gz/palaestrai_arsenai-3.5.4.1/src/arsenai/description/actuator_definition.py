from dataclasses import dataclass
from typing import List


@dataclass
class ActuatorDefinition:
    uid: str
    actuator_ids: List[str]
