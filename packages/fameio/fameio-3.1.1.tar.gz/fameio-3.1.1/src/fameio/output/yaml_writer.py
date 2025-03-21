# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import yaml

from fameio.logs import log

ERR_WRITE_EXCEPTION = "Failed to save dictionary to YAML file `{}`"
INFO_DESTINATION = "Saving scenario to file at {}"


def data_to_yaml_file(data: dict, file_path: Path) -> None:
    """
    Save the given data to a YAML file at given path

    Args:
        data: to be saved to yaml file
        file_path: at which the file will be created
    """
    log().info(INFO_DESTINATION.format(file_path))
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, encoding="utf-8")
    except Exception as e:
        raise RuntimeError(ERR_WRITE_EXCEPTION.format(file_path)) from e
