"""This module contains the :func:`analyze_experiment` that is used
to determine the number of required runs and to split parameters into
independent and control variables.

"""

from ..description import ParameterDefinition
from . import LOG


def analyze_experiment(experiment):
    """Analyze an experiment.

    Calculates and returns the number of required runs if every
    possible parameter configuration is tested. Also creates a
    parameter definition that stores independent and control variables
    and their configuration.

    Parameters
    ----------
    experiment: Experiment
        The :class:`Experiment` object containing the content of the
        experiment file.

    Returns
    -------
    ParameterDefinition
        The parameter definition created from the analysis of the
        experiment object.

    """
    params = ParameterDefinition()

    LOG.info(
        "Experiment '%s' has %d run phase(s).",
        experiment.uid,
        len(experiment.schedule),
    )
    for idx, phase in enumerate(experiment.schedule):
        if len(phase) > 1:
            LOG.warning(
                "Phase %d has more than one (=%d) phase definitions. "
                "Every definition after the first one will be ignored.",
                idx,
                len(phase),
            )
        phase_def = phase[list(phase.keys())[0]]

        _analyze_phase(idx, phase_def, params)
        _analyze_sensors_and_actuators(idx, phase_def, params)

    LOG.info(
        "Experiment '%s' allows %d different configuration(s).",
        experiment.uid,
        params.required_runs,
    )
    return params


def _analyze_phase(idx, phase_def, params):
    """Analyze entries of a phase.

    Splits the configuration into independent variables and control
    variables.

    Variable keys have the format: idx.factor._, where idx is the index
    of the current phase, factor is one of `environments`, `agents`,
    `simulation`, or `phase_config`. The underscore is not used here
    but it is added to have the same schema for all variables.

    Parameters
    ----------
    idx: int
        Index of the current phase.
    phase_def: dict
        The definition of the current phase from the experiment file.
    params: ParameterDefinition
        The parameter definition where the variables will be added.

    """
    for factor in ["environments", "agents", "simulation", "phase_config"]:
        if factor in phase_def:
            levels = len(phase_def[factor])

            key = f"{idx}.{factor}._"
            param_cfg = dict()
            for lidx, level in enumerate(phase_def[factor]):
                param_cfg[lidx] = level
            if levels > 1:
                params.add_independent_variable(key, param_cfg)
            else:
                params.add_control_variable(key, param_cfg)

            LOG.debug(
                "Phase %d: Factor '%s' has %d level(s).",
                idx,
                factor,
                levels,
            )


def _analyze_sensors_and_actuators(idx, phase_def, params):
    """Analyze sensor and actuator entries of a phase.

    Splits the configuration into independent variables and control
    variables.

    Variable keys have the format: idx.factor.agent_key, where idx is
    the index of the current phase, factor is one of `sensors` or
    `actuators`. Since sensors are defined per-agent, the agent_key
    specifies to which agent the configuration belongs to.

    Parameters
    ----------
    idx: int
        Index of the current phase.
    phase_def: dict
        The definition of the current phase from the experiment file.
    params: ParameterDefinition
        The parameter definition where the variables will be added.

    """
    for factor in ["sensors", "actuators"]:
        if factor not in phase_def:
            continue

        for agent_key, defs in phase_def[factor].items():
            levels = len(defs)

            key = f"{idx}.{factor}.{agent_key}"
            param_cfg = dict()
            for lidx, level in enumerate(defs):
                param_cfg[lidx] = level

            if levels > 1:
                params.add_independent_variable(key, param_cfg)
            else:
                params.add_control_variable(key, param_cfg)

            LOG.debug(
                "Phase %d: Factor '%s' has %d level(s) for agent %s.",
                idx,
                factor,
                levels,
                agent_key,
            )
