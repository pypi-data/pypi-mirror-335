# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import copy
from argparse import ArgumentParser, ArgumentTypeError, BooleanOptionalAction, Namespace
from enum import Enum
from pathlib import Path
from typing import Optional, Any, Union

from fameio.cli.options import TimeOptions, ResolveOptions, Options
from fameio.logs import LogLevel

_ERR_INVALID_MERGING_DEFAULT = "Invalid merge-times default: needs list of 3 integers separated by spaces but was: '{}'"

_OPTION_ARGUMENT_NAME: dict[str, Union[Options, dict]] = {
    "file": Options.FILE,
    "log": Options.LOG_LEVEL,
    "logfile": Options.LOG_FILE,
    "output": Options.OUTPUT,
    "encoding": Options.INPUT_ENCODING,
    "agents": Options.AGENT_LIST,
    "single_export": Options.SINGLE_AGENT_EXPORT,
    "memory_saving": Options.MEMORY_SAVING,
    "time": Options.TIME,
    "input_recovery": Options.INPUT_RECOVERY,
    "complex_column": Options.RESOLVE_COMPLEX_FIELD,
    "merge_times": Options.TIME_MERGING,
}


def add_file_argument(parser: ArgumentParser, default: Optional[Path], help_text: str) -> None:
    """
    Adds 'file' argument to the provided `parser` with the provided `help_text`.
    If a default is not specified, the argument is required (optional otherwise)

    Args:
        parser: to add the argument to
        default: optional, if it is a valid Path, it is added as default and the argument becomes optional
        help_text: to be displayed
    """
    if default is not None and isinstance(default, (Path, str)):
        parser.add_argument("-f", "--file", type=Path, required=False, default=default, help=help_text)
    else:
        parser.add_argument("-f", "--file", type=Path, required=True, help=help_text)


def add_select_agents_argument(parser: ArgumentParser, default: list[str]) -> None:
    """Adds optional repeatable string argument 'agent' to given `parser`"""
    help_text = "Provide list of agents to extract (default=None)"
    parser.add_argument("-a", "--agents", nargs="*", type=str, default=default, help=help_text)


def add_logfile_argument(parser: ArgumentParser, default: Path) -> None:
    """Adds optional argument 'logfile' to given `parser`"""
    help_text = "provide logging file (default=None)"
    parser.add_argument("-lf", "--logfile", type=Path, default=default, help=help_text)


def add_output_argument(parser: ArgumentParser, default_value, help_text: str) -> None:
    """Adds optional argument 'output' to given `parser` using the given `help_text` and `default_value`"""
    parser.add_argument("-o", "--output", type=Path, default=default_value, help=help_text)


def add_log_level_argument(parser: ArgumentParser, default_value: str) -> None:
    """Adds optional argument 'log' to given `parser`"""
    help_text = f"choose logging level (default: {default_value})"
    # noinspection PyTypeChecker
    parser.add_argument(
        "-l",
        "--log",
        default=default_value,
        choices=[level.name for level in LogLevel if level not in [LogLevel.PRINT, LogLevel.WARN]],
        type=str.upper,
        help=help_text,
    )


def add_encoding_argument(parser: ArgumentParser, default_value: Optional[str], help_text: str) -> None:
    """Adds optional argument `enc` to given parser"""
    parser.add_argument("-enc", "--encoding", type=str, default=default_value, help=help_text)


def add_single_export_argument(parser: ArgumentParser, default_value: bool) -> None:
    """Adds optional repeatable string argument 'agent' to given `parser`"""
    help_text = "Enable export of single agents (default=False)"
    parser.add_argument(
        "-se",
        "--single-export",
        default=default_value,
        action="store_true",
        help=help_text,
    )


def add_memory_saving_argument(parser: ArgumentParser, default_value: bool) -> None:
    """Adds optional bool argument to given `parser` to enable memory saving mode"""
    help_text = "Reduces memory usage profile at the cost of runtime (default=False)"
    parser.add_argument(
        "-m",
        "--memory-saving",
        default=default_value,
        action="store_true",
        help=help_text,
    )


def add_resolve_complex_argument(parser: ArgumentParser, default_value: Union[ResolveOptions, str]):
    """Instructs given `parser` how to deal with complex field outputs"""
    default_value = default_value if isinstance(default_value, ResolveOptions) else ResolveOptions[default_value]
    help_text = f"How to deal with complex index columns? (default={default_value})"
    parser.add_argument(
        "-cc",
        "--complex-column",
        type=ResolveOptions.instantiate,
        default=default_value,
        choices=ResolveOptions,
        help=help_text,
    )


def add_time_argument(parser: ArgumentParser, default_value: Union[TimeOptions, str]) -> None:
    """Adds optional argument to given `parser` to define conversion of TimeSteps"""
    default_value = default_value if isinstance(default_value, TimeOptions) else TimeOptions[default_value]
    help_text = "Apply conversion of time steps to given format (default=UTC)"
    parser.add_argument(
        "-t",
        "--time",
        type=TimeOptions.instantiate,
        default=default_value,
        choices=TimeOptions,
        help=help_text,
    )


def add_merge_time_argument(parser: ArgumentParser, defaults: Optional[list[int]] = None) -> None:
    """Adds optional three-fold argument for merging of TimeSteps to given `parser`"""
    if defaults is None:
        defaults = []
    if (
        not isinstance(defaults, list)
        or len(defaults) not in [0, 3]
        or not all(isinstance(value, int) for value in defaults)
    ):
        raise ArgumentTypeError(_ERR_INVALID_MERGING_DEFAULT.format(repr(defaults)))

    help_text = (
        "Merge multiple time steps to have less lines per output file. "
        "Provide 3 integers separated by spaces that resemble FocalPoint, StepsBefore, and StepsAfter."
    )
    parser.add_argument("-mt", "--merge-times", type=int, nargs=3, default=defaults, help=help_text)


def add_inputs_recovery_argument(parser: ArgumentParser, default: bool) -> None:
    """Adds optional bool argument to given `parser` to recover inputs"""
    help_text = "If --(no-)input-recovery is specified, (no) inputs will be recovered"
    parser.add_argument(
        "--input-recovery",
        action=BooleanOptionalAction,
        default=default,
        help=help_text,
    )


def update_default_config(config: Optional[dict], default: dict) -> dict:
    """Returns `default` config with updated fields received from `config`"""
    result = copy.deepcopy(default)
    if config:
        for name, option in config.items():
            result[name] = option
    return result


def map_namespace_to_options_dict(parsed: Namespace) -> dict[Options, Any]:
    """
    Maps given parsing results to their corresponding configuration option

    Args:
        parsed: result of a parsing

    Returns:
        Map of each parsed argument to their configuration option
    """
    return _map_namespace_to_options(parsed, _OPTION_ARGUMENT_NAME)


def _map_namespace_to_options(parsed: Namespace, names_to_options: dict[str, Enum]) -> dict[Options, Any]:
    """
    Maps given parsing results to their corresponding configuration option; elements that cannot be mapped are ignored.
    If a configuration option has inner elements, these well be also read and added as inner dictionary.

    Args:
        parsed: result of a parsing
        names_to_options: dict to search for configuration option specifications

    Returns:
         Map parsed arguments to their configuration option if they exist in the given `names_to_options` dict
    """
    config = {}
    for name, value in vars(parsed).items():
        option = names_to_options.get(name, None)
        if option:
            if isinstance(option, dict):
                inner_element_map = option["inner_elements"]
                option = option["name"]
                value = _map_namespace_to_options(parsed, inner_element_map)
            config[option] = value
    return config
