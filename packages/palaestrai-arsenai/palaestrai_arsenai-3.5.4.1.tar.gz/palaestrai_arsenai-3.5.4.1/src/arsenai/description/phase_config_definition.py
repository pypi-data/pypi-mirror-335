from dataclasses import dataclass


@dataclass
class PhaseConfigDefinition:
    uid: str
    mode: str
    worker: int
    episodes: int
