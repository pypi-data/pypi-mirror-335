from __future__ import annotations
from typing import List, Dict, Union
from dataclasses import dataclass


@dataclass
class AgentDefinition:
    uid: str
    name: str
    load: dict
    replay: List[Dict[str, Union[str, int]]]
    brain_name: str
    brain_params: dict
    muscle_name: str
    muscle_params: dict
    objective_name: str
    objective_params: dict
