#!/usr/bin/env python
import sys

from fameio.scripts.convert_results import DEFAULT_CONFIG as DEFAULT_CONVERT_CONFIG
from fameio.scripts.convert_results import run as convert_results
from fameio.scripts.make_config import run as make_config
from fameio.cli.convert_results import handle_args as handle_convert_results_args
from fameio.cli.make_config import handle_args as handle_make_config_args


# noinspection PyPep8Naming
def makeFameRunConfig():
    run_config = handle_make_config_args(sys.argv[1:])
    make_config(run_config)


# noinspection PyPep8Naming
def convertFameResults():
    run_config = handle_convert_results_args(sys.argv[1:], DEFAULT_CONVERT_CONFIG)
    convert_results(run_config)
