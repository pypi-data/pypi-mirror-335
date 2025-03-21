from dataclasses import dataclass


@dataclass
class EnvironmentDefinition:
    uid: str
    environment_name: str
    environment_params: dict
    environment_uid: str
    reward_name: str
    reward_params: dict
    state_transformer_name: str
    state_transformer_params: dict
