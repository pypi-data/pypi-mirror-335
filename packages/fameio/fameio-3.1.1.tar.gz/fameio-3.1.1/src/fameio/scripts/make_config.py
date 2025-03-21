#!/usr/bin/env python
import sys
from pathlib import Path

from fameio.cli.make_config import handle_args, CLI_DEFAULTS as DEFAULT_CONFIG
from fameio.cli.options import Options
from fameio.cli import update_default_config
from fameio.input.loader import load_yaml, validate_yaml_file_suffix
from fameio.logs import fameio_logger, log
from fameio.input.scenario import Scenario
from fameio.input.validator import SchemaValidator
from fameio.input.writer import ProtoWriter


def run(config: dict = None) -> None:
    """Executes the main workflow for the building of a FAME configuration file"""
    config = update_default_config(config, DEFAULT_CONFIG)
    fameio_logger(log_level_name=config[Options.LOG_LEVEL], file_name=config[Options.LOG_FILE])

    file = config[Options.FILE]
    validate_yaml_file_suffix(Path(file))
    scenario = Scenario.from_dict(load_yaml(Path(file), encoding=config[Options.INPUT_ENCODING]))
    SchemaValidator.check_agents_have_contracts(scenario)

    timeseries_manager = SchemaValidator.validate_scenario_and_timeseries(scenario)
    writer = ProtoWriter(config[Options.OUTPUT], timeseries_manager)
    writer.write_validated_scenario(scenario)

    log().info("Configuration completed.")


if __name__ == "__main__":
    run_config = handle_args(sys.argv[1:])
    run(run_config)
