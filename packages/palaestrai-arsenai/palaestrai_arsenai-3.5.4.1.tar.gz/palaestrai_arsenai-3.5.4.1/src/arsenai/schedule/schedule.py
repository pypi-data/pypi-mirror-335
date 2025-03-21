# from arsenai.schedule.phase import Phase

from . import LOG
from .phase import Phase


class Schedule:
    """This class stores information about the schedule for a specific
    experiment run.

    """

    def __init__(self, blueprint: list):
        self._blueprint: list = blueprint
        self.phases: list = list()

    def populate(self):
        for phase_idx, phase_def in enumerate(self._blueprint):
            name = list(phase_def.keys())[0]
            phase = Phase(phase_idx, name, phase_def[name])
            phase.populate()
            self.phases.append(phase)

    def build(self, experiment, design_idx):
        for phase in self.phases:
            for request in phase.requests:
                LOG.debug("Processing request: %s", request)
                prev_phase = self.phases[request["from_phase"]]
                attr = getattr(phase, request["what"])
                if "entry" in request:
                    attr[request["level"]][request["entry"]] = getattr(
                        prev_phase, request["what"]
                    )[request["index"]]
                else:
                    prev_attr = getattr(prev_phase, request["what"])
                    if isinstance(prev_attr, list):
                        attr[request["level"]] = prev_attr[request["level"]]
                    else:
                        setattr(phase, request["what"], prev_attr)
            phase.build(experiment, design_idx)

    def as_list(self):
        schedule = list()
        for phase in self.phases:
            schedule.append(phase.as_dict())
        return schedule
