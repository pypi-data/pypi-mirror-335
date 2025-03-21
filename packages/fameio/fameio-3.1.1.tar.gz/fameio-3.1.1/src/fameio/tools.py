# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import Any, Union


def keys_to_lower(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Returns new dictionary content of given `dictionary` but its top-level `keys` in lower case"""
    return {keys.lower(): value for keys, value in dictionary.items()}


def ensure_is_list(value: Any) -> list:
    """Returns a list: Either the provided `value` if it is a list, or a new list containing the provided value"""
    if isinstance(value, list):
        return value
    return [value]


def ensure_path_exists(path: Union[Path, str]):
    """Creates a specified path if not already existent"""
    Path(path).mkdir(parents=True, exist_ok=True)


def clean_up_file_name(name: str) -> str:
    """Returns given `name` with replacements defined in `replace_map`"""
    replace_map = {" ": "_", ":": "_", "/": "-"}
    return name.translate(str.maketrans(replace_map))
