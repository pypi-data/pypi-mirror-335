"""This module contains the :func:`create_design` that creates an
experiment design for a specific parameter definition.

"""

import doepy.build
import numpy as np
import pandas as pd

from . import LOG


def create_design(parameter_definition, max_runs, n_iter=1000):
    """Create a sampling design.

    If the number of required runs is lower than the maximal number of
    allowed runs, a full-factorial design is created and returned.

    Otherwise, a subset of the full-factorial design will be optimized
    according to the maximin metric.

    Parameters
    ----------
    parameter_definition: ParameterDefinition
        The definition of parameters of the experiment, containing
        independent and control variables.
    max_runs: int
        The maximal number of runs to create. Can be defined in the
        experiment file.
    n_iter: int, optional
        The number of iterations of the optimizer.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the experiment design for the
        independent variables.

    """
    design = doepy.build.full_fact(parameter_definition.ind_vars)

    if max_runs < 0 or parameter_definition.required_runs <= max_runs:
        return design
    else:
        sample = design.sample(n=max_runs)
        sample_values = sample.values
        sample_optimized = _optimize(sample_values, design.values, n_iter)
        design = pd.DataFrame(
            data=sample_optimized, index=sample.index, columns=sample.columns
        )

    return design


def _optimize(design, original, n_iter):
    """Optimize a design with an evolutionary algorithm (EA).

    The (1+1)-EA uses the maximin metric to optimize the design.

    Parameters
    ----------
    design: np.ndarray
        The initial sampling design.
    original: np.ndarray
        The full-factorial design to sample from.
    n_iter: int
        The number of iterations of the EA.

    Returns
    -------
    np.ndarray
        The final design with the best score according to maximin.

    """

    candidate = design
    current1 = candidate.copy()

    for idx in range(n_iter):
        current2 = candidate.copy()

        # Create offspring
        _mutate(current1, original)
        _mutate(current2, original)

        if _isbetter(current1, candidate):
            candidate = current1
            LOG.debug("Candidate 1 has a better design in iteration %d.", idx)
        if _isbetter(current2, candidate):
            candidate = current2
            LOG.debug("Candidate 2 has a better design in iteration %d.", idx)

    return candidate


def _mutate(design, original):
    """Mutate a given design from the original (full) design.

    Randomly choose a point in the design matrix and mutate the design
    point within the level's range. First, by extracting the ranges of
    the factors from the design, randomly choose a point in the design:
    `design[idx_row][idx_col]`, and, finally, randomize it within the
    range.

    Parameters
    ----------
    design: np.ndarray
        The array of the design to be mutated.
    original: np.ndarray
        The array of the full factorial design.

    """
    high_ranges = np.zeros(design.shape[1])
    low_ranges = np.zeros(design.shape[1])

    for col in range(design.shape[1]):
        high_ranges[col] = np.max(original[:, col])
        low_ranges[col] = np.min(original[:, col])

    # TODO: seed the rng
    idx_row = np.random.randint(design.shape[0])
    idx_col = np.random.randint(design.shape[1])

    design[idx_row][idx_col] = np.random.randint(
        low_ranges[idx_col], high_ranges[idx_col] + 1
    )


def _isbetter(design1, design2, mode="maximin", p=8):
    """Return whether the first design is better than the second.

    The designs are rated based on the maximin metric (see equation 8.9
    in `Statistische Versuchsplanung: Design of Experiments (DoE) by
    Siebertz et al.).

    Notes
    -----
        The p value is chosen experimentally, considering the 0 - 1
        range of the current factor levels, it should be examined
        according to the factors and their ranges to achieve a better
        distribution of the points

    Parameters
    ----------
    design1: np.ndarray
        The first design to rate.
    design2: np.ndarray
        The second design to rate and to compare with.
    mode: str, optional
        The metric to use. Currently, only `maximin` is possible.
    p: int, optional
        The p value used to calculate the maximin.

    Returns
    -------
    bool
        True if design1 is better, False otherwise.

    """
    if mode == "maximin":
        maximinp_design1 = sum(_pdist(design1) ** -p) ** (1 / p)
        maximinp_design2 = sum(_pdist(design2) ** -p) ** (1 / p)
    else:
        raise ValueError(f"Mode {mode} is not supported.")

    return maximinp_design1 < maximinp_design2


def _pdist(design):
    """Calculate the point-wise distance of the design.

    Parameters
    ----------
    design: np.ndarray
        The design for which the distance is calculated.

    Returns
    -------
    np.ndarray
        Point-wise distances of the design's points.

    """
    num, dim = design.shape
    distances = list()

    for idx in range(num - 1):
        for jdx in range(idx + 1, num):
            distances.append(
                sum((design[jdx, :] - design[idx, :]) ** 2) ** 0.5
            )

    return np.array(distances)
