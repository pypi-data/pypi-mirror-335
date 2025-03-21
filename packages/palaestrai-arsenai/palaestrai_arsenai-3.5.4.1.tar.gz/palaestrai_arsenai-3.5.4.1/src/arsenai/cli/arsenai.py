#!usr/bin/env python3
# arsenai.py -- Manager CLI for ARL DoE generation for palaestrAI.
# Copyright (C) 2020  OFFIS, All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.

import sys

import click
import palaestrai
import pkg_resources
import setproctitle
from palaestrai.cli.manager import init_logger
from palaestrai.core import RuntimeConfig

from arsenai.api import fnc_generate


@click.group()
@click.option(
    "-c",
    "--config",
    type=click.Path(),
    help="Supply custom runtime configuration file. "
    "(Default search path: %s)"
    % (palaestrai.core.runtime_config._RuntimeConfig.CONFIG_FILE_PATHS),
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increases the program verbosity, can be given numerous times: "
    "-v prints also INFO messages, and -vv emits DEBUG output."
    "output",
)
@click.version_option(pkg_resources.require("palaestrai-arsenai")[0].version)
def main(config=None, verbose=0):
    setproctitle.setproctitle(" ".join(sys.argv))

    if config:
        try:
            with open(config, "r") as fp:
                RuntimeConfig().load(fp)
        except OSError as err:
            click.echo(
                f"ERROR: Could not load config from {config}: {err}.",
                file=sys.stderr,
            )
            exit(1)
    else:
        try:
            RuntimeConfig().load()
        except FileNotFoundError as err:
            click.echo(
                f"Please create a runtime config: {err}.\n"
                "Will continue with built-in defaults.",
                file=sys.stderr,
            )
    init_logger(verbose)


@main.command()
@click.argument(
    "experiment_file",
    type=click.Path(
        exists=True, dir_okay=False, readable=True, allow_dash=True
    ),
)
def generate(experiment_file):
    click.echo(f"Reading experiment file: {experiment_file}.")

    fnc_generate.generate(experiment_file)

    click.echo("ArsenAI finished!")
