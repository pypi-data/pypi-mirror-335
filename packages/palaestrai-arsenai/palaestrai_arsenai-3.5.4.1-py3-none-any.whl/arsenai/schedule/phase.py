class Phase:
    """This class stores information of a specific phase in a
    schedule.

    """

    def __init__(self, phase_idx: int, name: str, blueprint: dict):
        self.phase_idx: int = phase_idx
        self.name: str = name
        self.blueprint: dict = blueprint
        self.environments: list = None
        self.agents: list = None
        self.simulation: dict = None
        self.phase_config: dict = None

        self.sensors: dict = None
        self.actuators: dict = None

        self._phase: dict = dict()
        self.requests: list = list()

    def populate(self):
        self.environments = self._read_blueprint("environments")
        self.agents = self._read_blueprint("agents")
        self.simulation = self._read_blueprint("simulation")
        self.phase_config = self._read_blueprint("phase_config")
        self.sensors = self._read_blueprint("sensors")
        self.actuators = self._read_blueprint("actuators")

    def _read_blueprint(self, key):
        content = self.blueprint.get(key, ["$req($prev)"])
        if isinstance(content, list):
            for level_idx, level in enumerate(content):
                if isinstance(level, list):
                    # environments, agents
                    for entry_idx, entry in enumerate(level):
                        request = {}
                        if "$req" in entry:
                            request = {
                                "level": level_idx,
                                "what": key,
                                "entry": entry_idx,
                                "replace": entry,
                            }
                            args = (
                                entry.split("(")[-1].split(")")[0].split(",")
                            )

                            for arg in args:
                                if "phase" in arg:
                                    request["from_phase"] = int(
                                        arg.split("=")[-1]
                                    )
                                elif "index" in arg:
                                    request["index"] = int(arg.split("=")[-1])
                                else:
                                    raise ValueError(
                                        f"Unknown argument: {arg}"
                                    )

                        if request:
                            self.requests.append(request)

                elif isinstance(level, dict):
                    # sensors, actuators
                    pass

                elif isinstance(level, str):
                    # everything else
                    request = {}
                    if "$req" in level:
                        request = {
                            "level": level_idx,
                            "what": key,
                            "replace": level,
                        }
                        args = level.split("(")[-1].split(")")[0].split(",")
                        for arg in args:
                            if arg == "$prev":
                                request["from_phase"] = self.phase_idx - 1
                            elif "phase" in arg:
                                request["from_phase"] = int(arg.split("=")[0])
                            else:
                                raise ValueError(f"Unknown argument: {arg}")
                    if request:
                        self.requests.append(request)
            # content = list()

        # if isinstance(content, str):
        #     # everything else, have no index
        #     if "$req" in content:
        #         args = content.split("(")[-1].split(")")[0]
        #         args = args.split(",")
        #         request = {"index": 0, "what": key}
        #         for arg in args:
        #             if arg == "$prev":
        #                 request["from_phase"] = self.phase_idx - 1
        #             elif "phase" in arg:
        #                 _, target = arg.split("=")
        #                 request["from_phase"] = int(target)
        #             else:
        #                 raise ValueError(f"Unknown argument: {arg}")
        #         self.requests.append(request)
        #     content = list()

        return content

    def build(self, generator, design_idx):
        design = generator.design.iloc[design_idx]

        for factor in [
            "environments",
            "agents",
            "simulation",
            "phase_config",
        ]:
            config = None
            for name, level in design.items():
                if factor not in name:
                    continue
                _phase_idx, _, _ = name.split(".")
                if int(_phase_idx) != self.phase_idx:
                    continue
                user_key = getattr(self, factor)[int(level)]
                config = generator.experiment.get_definition(
                    factor, user_key, self.name
                )
                setattr(self, factor, user_key)
                break

            if config is None:
                user_keys = getattr(self, factor)
                if isinstance(user_keys, list):
                    user_keys = user_keys[0]
                # user_keys = getattr(self, factor)[0]
                if isinstance(user_keys, str):
                    user_keys = [user_keys]

                config = generator.experiment.get_definition(
                    factor, user_keys, self.name
                )
            self._phase[factor] = config

        for factor in ["sensors", "actuators"]:
            for agent_key, defs in getattr(self, factor).items():
                # agent_key = agent_def["uid"]
                level = 0
                for (
                    name,
                    dlevel,
                ) in design.items():
                    _phase_idx, _factor, _agent_key = name.split(".")
                    if (
                        factor != _factor
                        or agent_key != _agent_key
                        or int(_phase_idx) != self.phase_idx
                    ):
                        continue
                    level = int(dlevel * (len(getattr(self, factor)) - 1))
                    break

                config = generator.experiment.get_definition(
                    factor, defs[level], self.name
                )
                for agent_cfg in self._phase["agents"]:
                    if agent_cfg["uid"] == agent_key:
                        agent_cfg[factor] = list()
                        for env_cfg in self._phase["environments"]:
                            env_uid = [val for val in env_cfg.values()][0][
                                "uid"
                            ]
                            if env_uid not in config:
                                continue
                            for uid in config[env_uid]:
                                if not str(uid).startswith(env_uid):
                                    key = f"{env_uid}.{uid}"
                                else:
                                    key = uid
                                if key not in agent_cfg[factor]:
                                    agent_cfg[factor].append(key)
                # if agent
        for agent_cfg in self._phase["agents"]:
            del agent_cfg["uid"]

    def as_dict(self):
        return {self.name: self._phase}
