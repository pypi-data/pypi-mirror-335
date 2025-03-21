#!/usr/bin/env python
import sys
from pathlib import Path

import pandas as pd

from fameio.cli.convert_results import handle_args, CLI_DEFAULTS as DEFAULT_CONFIG
from fameio.cli.options import Options
from fameio.cli import update_default_config
from fameio.logs import log_critical_and_raise, fameio_logger, log
from fameio.output.agent_type import AgentTypeLog
from fameio.output.conversion import apply_time_option, apply_time_merging
from fameio.output.csv_writer import CsvWriter
from fameio.output.data_transformer import DataTransformer, INDEX
from fameio.output.input_dao import InputDao
from fameio.output.output_dao import OutputDAO
from fameio.output.reader import Reader
from fameio.output.yaml_writer import data_to_yaml_file

ERR_OUT_OF_MEMORY = "Out of memory. Retry result conversion using `-m` or `--memory-saving` option."
ERR_MEMORY_SEVERE = "Out of memory despite memory-saving mode. Reduce output interval in `FAME-Core` and rerun model."

WARN_OUTPUT_MISSING = "Provided file did not contain any output data, only input recovery available."

INFO_MEMORY_SAVING = "Memory saving mode enabled: Disable on conversion of small files for performance improvements."
INFO_RECOVERY = "Recovering inputs..."
INFO_CONVERSION = "Applying time conversion and merging options to extracted files..."


def _extract_data(config: dict) -> bool:
    """Extracts, converts, and saves the converted data; Returns false if no result data was found"""
    file_path = Path(config[Options.FILE])
    output_writer = CsvWriter(config[Options.OUTPUT], file_path, config[Options.SINGLE_AGENT_EXPORT])
    agent_type_log = AgentTypeLog(requested_agents=config[Options.AGENT_LIST])
    data_transformer = DataTransformer.build(config[Options.RESOLVE_COMPLEX_FIELD])

    log().info("Reading and extracting data...")
    with open(file_path, "rb") as file_stream:
        reader = Reader.get_reader(file=file_stream, read_single=config[Options.MEMORY_SAVING])
        input_dao = InputDao()
        while data_storages := reader.read():
            if config[Options.INPUT_RECOVERY]:
                input_dao.store_inputs(data_storages)
            output = OutputDAO(data_storages, agent_type_log)
            for agent_name in output.get_sorted_agents_to_extract():
                log().debug(f"Extracting data for {agent_name}...")
                data_frames = output.get_agent_data(agent_name, data_transformer)
                if not config[Options.MEMORY_SAVING]:
                    apply_time_merging(data_frames, config[Options.TIME_MERGING])
                    apply_time_option(data_frames, config[Options.TIME])
                log().debug(f"Writing data for {agent_name}...")
                output_writer.write_to_files(agent_name, data_frames)

        if config[Options.INPUT_RECOVERY]:
            _recover_inputs(config, input_dao)
        if config[Options.MEMORY_SAVING]:
            _memory_saving_apply_conversions(config, output_writer)
        log().info("Data conversion completed.")
    return agent_type_log.has_any_agent_type()


def _recover_inputs(config: dict, input_dao: InputDao) -> None:
    """Reads scenario configuration from provided input_dao"""
    log().info(INFO_RECOVERY)
    timeseries, scenario = input_dao.recover_inputs()
    base_path = config[Options.OUTPUT] if config[Options.OUTPUT] is not None else "./"
    series_writer = CsvWriter(
        config_output=Path(base_path, "./recovered"), input_file_path=Path("./"), single_export=False
    )
    series_writer.write_time_series_to_disk(timeseries)
    data_to_yaml_file(scenario.to_dict(), Path(base_path, "./recovered/scenario.yaml"))


def _memory_saving_apply_conversions(config: dict, output_writer: CsvWriter) -> None:
    """Rewrite result files in memory saving mode: apply time-merging and time conversion options on a per-file basis"""
    log().info(INFO_CONVERSION)
    written_files = output_writer.pop_all_file_paths()
    for agent_name, file_path in written_files.items():
        parsed_data = {None: pd.read_csv(file_path, sep=";", index_col=INDEX)}
        apply_time_merging(parsed_data, config[Options.TIME_MERGING])
        apply_time_option(parsed_data, config[Options.TIME])
        output_writer.write_to_files(agent_name, parsed_data)


def run(config: dict = None) -> None:
    """Reads configured file in protobuf format and extracts its content to .CSV and .YAML file(s)"""
    config = update_default_config(config, DEFAULT_CONFIG)
    fameio_logger(log_level_name=config[Options.LOG_LEVEL], file_name=config[Options.LOG_FILE])
    if config[Options.MEMORY_SAVING]:
        log().info(INFO_MEMORY_SAVING)
    try:
        found_result_data = _extract_data(config)
        if not found_result_data:
            log().warning(WARN_OUTPUT_MISSING)
    except MemoryError:
        log_critical_and_raise(MemoryError(ERR_MEMORY_SEVERE if config[Options.MEMORY_SAVING] else ERR_OUT_OF_MEMORY))


if __name__ == "__main__":
    run_config = handle_args(sys.argv[1:])
    run(run_config)
