# SPDX-FileCopyrightText: 2024 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Union, Final

from fameio.input.metadata import Metadata, MetadataComponent, ValueContainer
from fameio.tools import keys_to_lower
from .exception import log_and_raise


class StringSet(Metadata):
    """Hosts a StringSet in the given format"""

    KEY_VALUES: Final[str] = "Values".lower()

    ValueType = Union[list[str], dict[str, dict]]
    StringSetType = dict[str, Union[dict, ValueType]]

    _ERR_KEY_MISSING = "Missing mandatory key '{}' in StringSet definition {}."

    def __init__(self, definitions=None):
        super().__init__(definitions)
        self._value_container: ValueContainer = ValueContainer(definitions)

    @classmethod
    def from_dict(cls, definition: StringSetType) -> StringSet:
        """Returns StringSet initialised from `definition`"""
        string_set = cls(definition)
        definition = keys_to_lower(definition)
        if cls.KEY_VALUES in definition:
            string_set._value_container = ValueContainer(definition[cls.KEY_VALUES])
        else:
            log_and_raise(cls._ERR_KEY_MISSING.format(cls.KEY_VALUES, definition))
        return string_set

    def _to_dict(self) -> dict[str, dict[str, dict[str, dict[str, dict]]]]:
        return {self.KEY_VALUES: self._value_container.to_dict()}

    @property
    def values(self) -> dict[str, MetadataComponent]:
        """Returns values and their associated MetadataComponent"""
        return self._value_container.values

    def is_in_set(self, key: str) -> bool:
        """Returns True if `key` is a valid name in this StringSet"""
        return self._value_container.has_value(key)
