"""This module contains util functions for reading experiment files and
writing run files.
"""

import collections.abc
import logging
import os

import ruamel
from ruamel.yaml.constructor import ConstructorError

LOG = logging.getLogger(__name__)


def load_experiment_file(stream):
    """Read the content of an experiment file from disk.

    The file to be loaded is expected to be a yaml file and needs to
    have a specific set of keys. See the example in
    `tests/fixtures/example_experiment.yml`.

    Parameters
    ----------
    stream: Union[str, TextIOWrapper]
        A filepath or a stream where to load the experiment from.

    Returns
    -------
    dict
        The content of the experiment file as *dict*.

    """
    LOG.debug("Loading experiment from %s.", stream)

    if isinstance(stream, str):
        try:
            stream = open(stream, "r")
        except OSError as err:
            LOG.error("Could not open experiment file: %s.", err)
            raise err
    try:
        content = ruamel.yaml.YAML(typ="safe", pure=True).load(stream)
    except ConstructorError as err:
        LOG.error("Coud not load experiment file: %s.", err)
        raise err
    finally:
        stream.close()
    LOG.debug("Loaded experiment: %s.", content)
    return content


def create_run_files(runs, experiment_id, output_path):
    """Write a list of run files to disk.

    Each run is a *dict* with a specific set of keys and values. The
    resulting file will be a run file that can be executed without
    further modification by palestrAI core.

    If you have specified an output path in your experiment file, the
    run files will be created at that location. Otherwise, a folder
    *_outputs* will be created in the current working directory.

    Parameters
    ----------
    runs: List[dict]
        A *list* of *dict*s where each dict represents an experiment
        run.
    experiment_id: str
        The `uid` of the experiment. Will be added to the filename
        of the runs.
    output_path: str
        The output path where the run files will be stored. Can be
        modified in the experiment file (key: output).

    """
    os.makedirs(output_path, exist_ok=True)
    yaml = ruamel.yaml.YAML(typ="safe", pure=True)
    for idx, run in enumerate(runs):
        filename = f"{experiment_id}_run-{idx}.yml"
        path = os.path.join(output_path, filename)

        with open(path, "w") as yaml_file:
            yaml.dump(run, yaml_file)


def update_dict(src, upd):
    """Recursive update of dictionaries.

    See stackoverflow:

        https://stackoverflow.com/questions/3232943/
        update-value-of-a-nested-dictionary-of-varying-depth

    """
    for key, val in upd.items():
        if isinstance(val, collections.abc.Mapping):
            src[key] = update_dict(src.get(key, dict()), val)
        else:
            src[key] = val
    return src
