# Self-improving ML / Amalgamation AI

## To contribute

Please check out [the contributing guideline](CONTRIBUTING.md).

## Overview of this repository

The aim of this code is to provide a framework for running machine learning experiments where the user
only needs to decide the high level settings of the experiment and the code will handle the rest. The
motivation is to create a structure where an AI system only needs to select the high level settings and
can avoid the need to write specific code for each experiment and, in this way, can "reason like a researcher".

To do this we create metaprograms. A metaprogram is a collection of high level settings which are interpreted
down to python code which runs the experiment. At the most basic level, a metaprogram consists of three core components:
a **model**, a **dataset**, and a **pipeline** (which is the code that interprets the metaprogram and runs the experiment).
Each of these components is defined by a yaml file in `configs/metaprogram/component`, these yaml files capture the various
settings that can be tweaked for each experiment (and provide a default value for each setting).

The upshot is we can run a variety of experiments with simple, high level, input. For example, to execute CLIP on cifar10 using
the default settings you would run:

```bash
python -B run_metaprogram.py +metaprogram/component/pipeline=execution +metaprogram/component/model=vlms/clip +metaprogram/component/dataset=classification/cifar +path=default
```

Here, the pipeline component is `execution` which runs a generic deep learning train/test pipeline,
the model component is `vlms/clip` which is the CLIP model, and the dataset component is `classification/cifar`
which is the cifar10 dataset. The final part, `path=default` defines the paths to the dataset,
model checkpoints, output files etc. It is **not** part of the metaprogram since the paths change on different
machines and are not a high level decision that a researcher or AI system needs to consider. (In fact, for an AI
system, we explicitly do not want it to be able to write files to anywhere on the system).

We can define the whole metaprogram in single yaml file, to run the same experiment as above you could run:

```bash
python -B run_metaprogram.py --config-name=metaprogram/example
```

## Project structure

(Not all components listed. Feel free to add others that seem important.)

```bash
├─ configs                      # General configuration files to be used with Hydra
    ├─ metaprogram              # Full metaprograms, written by hand, that can be executed
        ├─ component            # Configuration files that can be used to construct metaprograms
            ├─ dataset          # Dataset configuration files 
            ├─ model            # Model configuration files
            ├─ pipeline         # Pipeline configuration files
    ├─ path                     # Path configuration files
    ├─ sweep                    # Sweep configuration files (for util/sweeper.py)
├─ database                     # Code to handle databases of sequences for training LLMs
├─ job_launch                   # Code to launch multiple jobs and allocate the required resources to them
├─ engine                       # Stores all code that is needed to execute a single metaprogram
    ├─ data_pipe                # Code to handle data
        ├─ datasets             # Some methods to load data from disk
        ├─ resamplers           # Code for resampling
        ├─ sample_transforms    # Transforms to be applied on each data sample immediately after loading
    ├─ data_point               # All models input and output data stored in a dataclass named DataPoint
        ├─ DataPoints.py        # Different DataPoints for differnt data types
    ├─ hooks                    # Hooks for blueprint
    ├─ models                   # Models
        ├─ ComponentModel.py    # Base class of any other component models
        ├─ Model.py             # Class to interpret and assemble components
    ├─ pipelines                # Codes to execute training/testing
        ├─ execution.py         # Code to execute generic machine learning training/testing
├─ unit_test                    # Tests for every commit
├─ util                         # Utilities
    ├─ external_data_import     # Custom code for importing data from external sources
    ├─ how_tos                  # Example code for certain features of the codebase
    ├─ sweeper.py               # Generates large numbers of metaprograms (or problem statements) in one sweep
```

As a general philosophy, the user and the Planner need to edit only the yaml files under `/configs/` to try different settings.

## Running Multiple Experiments and Training the Metaprogrammer (i.e. the planner)

Three shell scripts are provided for training the metaprogrammer. It is recommended to try each of the commands
individually to understand what they do before executing them all at once. The scripts are

- `generate_ray_tune_data.sh`: creates training data made up of sequences of hyperparameter optimizations generated with [ray tune](https://docs.ray.io/en/latest/tune/index.html).
- `train_planner.sh`: trains the planner/metaprogrammer on the ray tune data.
- `generation_loop.sh`: uses the trained planner to generate new sequences according to the learned distribution.

More information on autoregressive training and system design can be found in the [wiki](https://github.com/automl-vt/self-improving/wiki/Planner).
