# Adversarial Resilience Learning --- Design of Experiments


## Introduction

Reproducibility of scientific experiments is more important than ever.
The Adversarial Resilience Learning -- Design of Experiments Suite *arsenAI* serves exactly this purpose.
It also enables to test different combinations of agents and environments in *palaestrAI*.

## Installation

ArsenAI is written in Python and available on [pypi.org](https://pypi.org/project/palaestrai-arsenai/).
A virtual environment is recommended. 
To install arsenAI, type:

```bash
pip install palaestrai-arsenai
```

To execute experiment runs, you also need palaestrAI.

## Usage

In the sources of arsenAI, there is an `example_experiment.yml` file. 
You find it in the folder tests/fixtures/. 
Download this file and save it to your current working directory.
To use arsenAI, simply type

```bash
arsenai generate ./example_experiment.yml
```

An output folder will be created (default: (current working directory)/_outputs)).
After the arsenAI command has finished, you will find palaestrAI run files and that directory, which can be executed with 
```
$ palaestrai start _outputs/Dummy\ Experiment_run-0.yml
```

You can copy the example file and modify it to your needs.

## Documentation

In the future, you will find a more comprehensive documentation on [docs.palaestr.ai](http://docs.palaestr.ai/experiments.html) 

## Copyright & Authors

All source code, except where otherwise mentioned, is Copyright (C) 2020, 2021, 2022 OFFIS e.V.
Contributing authors are listed in order of their appearance in the file `CONTRIBUTING.md`.



