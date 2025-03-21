from dataclasses import dataclass
from typing import List


@dataclass
class SensorDefinition:
    uid: str
    sensor_ids: List[str]
