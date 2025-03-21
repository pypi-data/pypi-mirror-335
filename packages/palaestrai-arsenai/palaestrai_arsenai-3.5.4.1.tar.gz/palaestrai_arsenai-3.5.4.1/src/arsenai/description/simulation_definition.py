from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SimulationDefinition:
    uid: str
    simulation_name: str
    conditions: List[Dict[str, dict]]
