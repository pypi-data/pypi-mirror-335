from dataclasses import dataclass


@dataclass
class RunConfigDefinition:
    condition_name: str
    condition_params: str
