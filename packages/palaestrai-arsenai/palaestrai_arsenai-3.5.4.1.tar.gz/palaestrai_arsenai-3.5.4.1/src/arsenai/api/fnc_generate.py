import logging
import os
from typing import Any, Dict, List, Union

from arsenai.generator import Experiment, Generator
from arsenai.util import create_run_files

LOG = logging.getLogger("arsenai.api")


def generate(
    experiment_file: Union[str, os.PathLike], no_disk_saving: bool = False
) -> List[Dict[str, Any]]:
    LOG.info(f"Reading experiment file: {experiment_file}.")

    experiment = Experiment.load(experiment_file)
    generator = Generator()
    runs, design = generator.generate(experiment)

    if not no_disk_saving:
        create_run_files(runs, experiment.uid, experiment.output_path)
        design.to_csv(
            os.path.join(
                experiment.output_path, f"{experiment.uid}_design.csv"
            )
        )

    LOG.info("ArsenAI finished!")
    return runs
