"""This module contains the experiment description for arsenAI."""

import os
from copy import deepcopy
from typing import List

from palaestrai.util import seeding

from ..description import (
    ActuatorDefinition,
    AgentDefinition,
    EnvironmentDefinition,
    PhaseConfigDefinition,
    RunConfigDefinition,
    SensorDefinition,
    SimulationDefinition,
)
from ..util import load_experiment_file
from . import LOG


class Experiment:
    """This object holds information about a single experiment."""

    def __init__(
        self,
        uid: str,
        version: str,
        seed: int,
        repetitions: str,
        max_runs: int,
        output_path: str,
        environment_definitions: List[EnvironmentDefinition],
        agent_definitions: List[AgentDefinition],
        sensor_definitions: List[SensorDefinition],
        actuator_definitions: List[ActuatorDefinition],
        simulation_definitions: List[SimulationDefinition],
        phase_config_definitions: List[PhaseConfigDefinition],
        run_config_definition: RunConfigDefinition,
        schedule: list,
    ):
        self.uid = uid
        (
            self.version_major,
            self.version_minor,
            self.version_patch,
        ) = (int(val) for val in version.split("."))
        self.rng, self.seed = seeding.np_random(seed)
        self.repetitions = repetitions
        self.max_runs = max_runs
        self.output_path = output_path
        self.environment_definitions = environment_definitions
        self.agent_definitions = agent_definitions
        self.sensor_definitions = sensor_definitions
        self.actuator_definitions = actuator_definitions
        self.simulation_definitions = simulation_definitions
        self.phase_config_definitions = phase_config_definitions
        self.run_config_definition = run_config_definition
        self.schedule = schedule

    def get_seed(self):
        # LOG.warning(
        #     "Reusing experiment seed for run! "
        #     "See arsenai.generator.experiment.py line 61.",
        # )
        return self.rng.randint(1_000_000)

    def get_version(self):
        return (
            f"{self.version_major}.{self.version_minor}.{self.version_patch}"
        )

    def get_schedule(self):
        return deepcopy(self.schedule)

    def get_run_config(self):
        return {
            "condition": {
                "name": self.run_config_definition.condition_name,
                "params": deepcopy(
                    self.run_config_definition.condition_params
                ),
            }
        }

    def get_definition(self, topic, user_key, phase_name):
        if topic == "environments":
            return self.get_environment_definition(user_key)
        if topic == "agents":
            return self.get_agent_definition(user_key, phase_name)
        if topic == "simulation":
            return self.get_simulation_definition(user_key)
        if topic == "phase_config":
            return self.get_phase_config_definition(user_key)
        if topic == "sensors":
            return self.get_sensor_definition(user_key)
        if topic == "actuators":
            return self.get_actuator_definition(user_key)

        raise KeyError(f"Unknown topic: '{topic}'")

    def get_environment_definition(self, uids):
        defs = list()
        for uid in uids:
            for envdef in self.environment_definitions:
                if envdef.uid == uid:
                    env_cfg = {
                        "environment": {
                            "name": envdef.environment_name,
                            "params": deepcopy(envdef.environment_params),
                            "uid": envdef.environment_uid,
                        },
                    }

                    # Reward may be emtpy
                    if envdef.reward_name:
                        env_cfg["reward"] = {
                            "name": envdef.reward_name,
                            "params": envdef.reward_params,
                        }

                    # State transformer may be empty
                    if envdef.state_transformer_name:
                        env_cfg["state_transformer"] = {
                            "name": envdef.state_transformer_name,
                            "params": envdef.state_transformer_params,
                        }
                    defs.append(env_cfg)
                    break
        return defs

    def get_agent_definition(self, uids, phase_name):
        defs = list()
        for uid in uids:
            for adef in self.agent_definitions:
                if adef.uid == uid:
                    data = {
                        "uid": adef.uid,
                        "name": adef.name,
                        "brain": {
                            "name": adef.brain_name,
                            "params": deepcopy(adef.brain_params),
                        },
                        "muscle": {
                            "name": adef.muscle_name,
                            "params": adef.muscle_params,
                        },
                        "objective": {
                            "name": adef.objective_name,
                            "params": adef.objective_params,
                        },
                        "load": (
                            adef.load[phase_name]
                            if phase_name in adef.load
                            else adef.load
                        ),
                        "replay": adef.replay,
                    }
                    try:
                        load = adef.load[phase_name]
                        if load:
                            data["load"] = load
                    except TypeError:
                        pass  # No load definition
                    except KeyError:
                        pass  # No load definition

                    defs.append(data)
                    break
        if len(defs) != len(uids):
            LOG.warning(
                "Could not determine all required configs: %s --> %s",
                uids,
                defs,
            )
        return defs

    def get_simulation_definition(self, uid):
        if isinstance(uid, list):
            uid = uid[0]
        for sdef in self.simulation_definitions:
            if sdef.uid == uid:
                return {
                    "name": sdef.simulation_name,
                    "conditions": deepcopy(sdef.conditions),
                }

    def get_phase_config_definition(self, uid):
        if isinstance(uid, list):
            uid = uid[0]
        for pcdef in self.phase_config_definitions:
            if pcdef.uid == uid:
                return {
                    "mode": pcdef.mode,
                    "worker": pcdef.worker,
                    "episodes": pcdef.episodes,
                }

    def get_sensor_definition(self, uid):
        for sendef in self.sensor_definitions:
            if sendef.uid == uid:
                return sendef.sensor_ids

        raise KeyError(
            f"Unknown sensor key '{uid}'. "
            "Please check your experiment schedule."
        )

    def get_actuator_definition(self, uid):
        for actdef in self.actuator_definitions:
            if actdef.uid == uid:
                return actdef.actuator_ids

        raise KeyError(
            f"Unknown actuator key '{uid}'. "
            "Please check your experiment schedule."
        )

    @staticmethod
    def load(stream):
        content = load_experiment_file(stream)

        env_definitions: List[EnvironmentDefinition] = []
        for uid, definition in content["definitions"]["environments"].items():
            environment = definition["environment"]
            reward = definition.setdefault("reward", {})
            state_trans = definition.setdefault("state_transformer", {})

            env_definitions.append(
                EnvironmentDefinition(
                    uid=uid,
                    environment_uid=environment.get("uid", "default_env"),
                    environment_name=environment["name"],
                    environment_params=environment.get("params", {}),
                    reward_name=reward.get("name", ""),
                    reward_params=reward.get("params", {}),
                    state_transformer_name=state_trans.get("name", ""),
                    state_transformer_params=state_trans.get("params", {}),
                )
            )

        return Experiment(
            uid=content.get("uid", content.get("id", None)),
            seed=content.get("seed", None),
            version=content.get("version", None),
            repetitions=content.get("repetitions", 1),
            max_runs=content.get("max_runs", -1),
            output_path=content.get(
                "output",
                os.path.abspath(os.path.join(os.getcwd(), "_outputs")),
            ),
            environment_definitions=env_definitions,
            agent_definitions=[
                AgentDefinition(
                    uid=key,
                    name=value.get("name", f"Unnamed Agent {idx}"),
                    load=value.get(
                        "load",
                        {},
                    ),
                    replay=value.get("replay", []),
                    brain_name=value["brain"]["name"],
                    brain_params=value["brain"].get("params", {}),
                    muscle_name=value["muscle"]["name"],
                    muscle_params=value["muscle"].get("params", {}),
                    objective_name=value["objective"]["name"],
                    objective_params=value["objective"].get("params", {}),
                )
                for idx, (key, value) in enumerate(
                    content["definitions"]["agents"].items()
                )
            ],
            sensor_definitions=[
                SensorDefinition(uid=key, sensor_ids=value)
                for key, value in content["definitions"]["sensors"].items()
            ],
            actuator_definitions=[
                ActuatorDefinition(uid=key, actuator_ids=value)
                for key, value in content["definitions"]["actuators"].items()
            ],
            simulation_definitions=[
                SimulationDefinition(
                    uid=key,
                    simulation_name=value["name"],
                    conditions=[cond for cond in value["conditions"]],
                )
                for key, value in content["definitions"]["simulation"].items()
            ],
            phase_config_definitions=[
                PhaseConfigDefinition(
                    uid=key,
                    mode=value["mode"],
                    worker=value["worker"],
                    episodes=value["episodes"],
                )
                for key, value in content["definitions"][
                    "phase_config"
                ].items()
            ],
            run_config_definition=RunConfigDefinition(
                condition_name=content["definitions"]["run_config"][
                    "condition"
                ]["name"],
                condition_params=content["definitions"]["run_config"][
                    "condition"
                ]["params"],
            ),
            schedule=content["schedule"],
        )
