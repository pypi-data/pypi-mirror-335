# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0


class InputError(Exception):
    """An error that occurred while parsing any kind of input"""


class SchemaError(InputError):
    """An error that occurred while parsing a Schema"""


class ScenarioError(InputError):
    """An error that occurred while parsing a Scenario"""


class YamlLoaderError(InputError):
    """An error that occurred while parsing a YAML file"""
