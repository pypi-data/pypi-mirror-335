import pandas as pd
from arsenai.description import ParameterDefinition
from arsenai.generator.analyzer import analyze_experiment
from arsenai.generator.designer import create_design
from arsenai.generator.experiment import Experiment
from arsenai.schedule.schedule import Schedule

from . import LOG


class Generator:
    """The palaestrAI experiment generator.

    The generator gets the content of an experiment file as an
    :class:`Experiment` object and creates several run files.

    """

    def __init__(self):
        self.required_runs = 1
        self.experiment: Experiment
        self.parameter_def: ParameterDefinition
        self.design: pd.DataFrame
        self.runs: list

    def generate(self, experiment):
        """Generate several runs from one experiment."""
        LOG.debug("Analyzing experiment: %s", experiment)
        self.experiment = experiment
        self.parameter_def = analyze_experiment(experiment)
        if self.parameter_def.required_runs > 1:
            self.design = create_design(
                self.parameter_def, experiment.max_runs
            )
        else:
            self.design = pd.DataFrame({"0._._": [0.0]})

        self.runs = self._build_runs()

        return self.runs, self.design

    def _build_runs(self):
        """Build the run configuration for all required runs.

        The number of runs generated depends on the design (i.e. the
        number of factors and levels or the variable max_runs) and the
        number of repetitions.

        Returns
        -------
        list:
            A list where each entry is a full run configuration.
        """
        runs = list()

        run_idx = 0
        for _ in range(self.experiment.repetitions):
            for idx in range(len(self.design)):
                run = dict()
                run["uid"] = f"{self.experiment.uid}-{run_idx}"
                run["experiment_uid"] = self.experiment.uid
                run["seed"] = self.experiment.get_seed()
                run["version"] = self.experiment.get_version()
                run["run_config"] = self.experiment.get_run_config()
                run["schedule"] = self._build_schedule(idx)
                runs.append(run)
                run_idx += 1
        return runs

    def _build_schedule(self, design_idx):
        """Build the schedule for a specific experiment run.

        This function creates the run configuration for a specific
        configuration of the experiment. All DoE-related information
        in the experiment-file-schedule will be replaced with the
        necessary information for the run file.

        Parameters
        ----------
        idx: int
            The index of the current design configuration.

        Returns
        -------
        schedule: list
            The schedule with all information required by palaestrAI
            to perform an experiment run.

        """
        schedule = Schedule(self.experiment.get_schedule())

        schedule.populate()

        schedule.build(self, design_idx)
        # schedule = self._popuplate_schedule(schedule)

        # for idx, phase in enumerate(schedule):
        #     phase_name = list(phase.keys())[0]
        #     self._build_phase(schedule, idx, phase_name, design_idx)

        # for idx, phase in enumerate(schedule):
        #     for agent_cfg in list(phase.values())[0]["agents"]:
        #         try:
        #             del agent_cfg["uid"]
        #         except KeyError:
        #             pass

        return schedule.as_list()

    # def _popuplate_schedule(self, schedule):
    #     """Generate the full schedule.

    #     The experiment file allows to skip entries in the schedule
    #     that are the same like in the previous phase. This function
    #     copies all information from the previous phase and updates
    #     with the current phase. This is saved as populated schedule.

    #     Parameters
    #     ----------
    #     schedule: list
    #         A list with all phase configs. The configs contain only
    #         minimal information.

    #     Returns
    #     -------
    #     list
    #         A list with all phase configs. The configs contain all
    #         information for that phase.

    #     """
    #     populated = list()

    #     prev_name = ""
    #     prev_config = dict()
    #     for idx, phase in enumerate(schedule):
    #         phase_name = list(phase.keys())[0]
    #         phase_config = phase[phase_name]
    #         if idx > 0:
    #             prev_config = deepcopy(populated[idx - 1][prev_name])
    #         else:
    #             prev_config = dict()

    #         phase_config = update_dict(prev_config, phase_config)
    #         populated.append({phase_name: phase_config})
    #         prev_name = phase_name
    #     return populated

    # def _build_phase(self, schedule, idx, phase_name, design_idx):
    #     """Build the config for a phase.

    #     Takes the input from the schedule defined in the experiment
    #     file and replaces all keys with actual configs. For each key
    #     that is subject of DoE, the corresponding config is identified
    #     with help of the experiment design.

    #     The schedule will be updated inplace.

    #     Parameters
    #     ----------
    #     schedule: list
    #         The populated schedule from the experiment file.
    #     idx: int
    #         The index of the current phase.
    #     phase_name: str
    #         The name of the current phase.
    #     design_idx: int
    #         The index of the current experiment run in the design.

    #     """
    #     phase_def = schedule[idx][phase_name]
    #     if idx > 0:
    #         prev_def = list(schedule[idx - 1].values())[0]
    #     else:
    #         prev_def = dict()

    #     design = self.design.iloc[design_idx]

    #     for factor in [
    #         "environments",
    #         "agents",
    #         "simulation",
    #         "phase_config",
    #     ]:

    #         config = None

    #         for name, level in design.items():
    #             if factor not in name:
    #                 continue

    #             _phase_idx, _, _ = name.split(".")
    #             if int(_phase_idx) != idx:
    #                 continue

    #             user_key = phase_def[factor][int(level)]
    #             config = self.experiment.get_definition(
    #                 factor, user_key, phase_name
    #             )
    #             break

    #         if config is None:
    #             copy_last = False
    #             if any([factor in val for val in design.index]) and prev_def:
    #                 copy_last = True
    #             if len(phase_def[factor]) == 1:
    #                 copy_last = False

    #             if copy_last:
    #                 config = deepcopy(prev_def[factor])
    #             else:
    #                 user_key = phase_def[factor][0]
    #                 config = self.experiment.get_definition(
    #                     factor, user_key, phase_name
    #                 )
    #         phase_def[factor] = config

    #     for factor in ["sensors", "actuators"]:
    #         for agent_key, defs in phase_def[factor].items():
    #             level = 0
    #             for name, dlevel in design.items():
    #                 _phase_idx, _factor, _agent_key = name.split(".")
    #                 if (
    #                     factor != _factor
    #                     or agent_key != _agent_key
    #                     or int(_phase_idx) != idx
    #                 ):
    #                     continue
    #                 level = int(dlevel * (len(phase_def[factor]) - 1))
    #                 break

    #             config = self.experiment.get_definition(
    #                 factor, defs[level], phase_name
    #             )
    #             for agent_cfg in phase_def["agents"]:
    #                 if agent_cfg["uid"] == agent_key:
    #                     agent_cfg[factor] = list()
    #                     for env_cfg in phase_def["environments"]:
    #                         env_uid = [val for val in env_cfg.values()][0][
    #                             "uid"
    #                         ]
    #                         if env_uid not in config:
    #                             continue

    #                         agent_cfg.setdefault(factor, list())
    #                         for uid in config[env_uid]:
    #                             sen_key = f"{env_uid}.{uid}"
    #                             if sen_key not in agent_cfg[factor]:
    #                                 agent_cfg[factor].append(sen_key)
    #     try:
    #         del phase_def["sensors"]
    #     except KeyError:
    #         pass
    #     try:
    #         del phase_def["actuators"]
    #     except KeyError:
    #         pass
