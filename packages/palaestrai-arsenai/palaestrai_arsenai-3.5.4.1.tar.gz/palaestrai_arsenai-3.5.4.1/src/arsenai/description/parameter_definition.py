"""This module contains the :class:`ParameterDefinition` that stores
the parameters and their configuration.

"""


class ParameterDefinition:
    """The definition of parameters for the design to create.

    Parameters can either be independent variables, which can change
    over the course of the experiment, or control variables, which stay
    the same for the whole experiment.

    The parameters are used by the generator to generate the design.

    Attributes
    ----------
    required_runs: int
        The number of runs required with the current parameter
        configuration.
    ind_vars: dict
        A *dict* containing IDs of independent variables and their
        configuration.
    ctrl_vars: dict
        A *dict* containing IDs of control variables and their
        configuration.

    """

    def __init__(self):
        self.required_runs = 1
        self.ind_vars = dict()
        self.ctrl_vars = dict()

    def add_independent_variable(self, name, levels):
        """Add an independent variable to the configuration.

        Depending on the number of levels, the required_runs will be
        increased.

        Parameters
        ----------
        name: str
            A unique but readable ID of the variable to add.
        levels: dict
            A *dict* with the configuration of each level.

        """
        self.required_runs *= len(levels)
        self.ind_vars[name] = levels

    def add_control_variable(self, name, level):
        """Add a control variable to the configuration.

        Parameters
        ----------
        name: str
            A unique but readable ID of the variable to add.
        level: dict
            A *dict* containing the configuration of the level.

        """
        self.ctrl_vars[name] = level
