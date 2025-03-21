# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional, Final, Union

from fameio.input import SchemaError
from fameio.input.metadata import Metadata, ValueContainer
from fameio.logs import log, log_error
from fameio.series import CSV_FILE_SUFFIX
from fameio.time import FameTime
from fameio.tools import keys_to_lower


class AttributeType(Enum):
    """Data types that Attributes can take"""

    INTEGER = auto()
    DOUBLE = auto()
    LONG = auto()
    TIME_STAMP = auto()
    STRING = auto()
    STRING_SET = auto()
    ENUM = auto()
    TIME_SERIES = auto()
    BLOCK = auto()

    def convert_string_to_type(self, value: str) -> Union[int, float, str]:
        """
        Converts a given string to this AttributeType's data format

        Args:
            value: string to be converted

        Returns:
            value converted to data format associated with AttributeType

        Raises:
            ValueError: if data conversion failed, e.g. due to improper string content
        """
        if self is AttributeType.INTEGER or self is AttributeType.LONG:
            return int(value)
        if self is AttributeType.DOUBLE:
            return float(value)
        if self is AttributeType.TIME_STAMP:
            return FameTime.convert_string_if_is_datetime(value)
        if self is AttributeType.ENUM or self is AttributeType.STRING or self is AttributeType.STRING_SET:
            return str(value)
        if self is AttributeType.TIME_SERIES:
            if isinstance(value, str) and Path(value).suffix.lower() == CSV_FILE_SUFFIX:
                return value
            return float(value)
        raise ValueError(f"String conversion not supported for '{self}'.")


class AttributeSpecs(Metadata):
    """Schema Definition of a single Attribute (with possible inner Attributes) of an agent"""

    _DISALLOWED_NAMES = ["value", "values", "metadata"]
    _SEPARATOR = "."

    KEY_MANDATORY: Final[str] = "Mandatory".lower()
    KEY_LIST: Final[str] = "List".lower()
    KEY_TYPE: Final[str] = "AttributeType".lower()
    KEY_NESTED: Final[str] = "NestedAttributes".lower()
    KEY_VALUES: Final[str] = "Values".lower()
    KEY_DEFAULT: Final[str] = "Default".lower()
    KEY_HELP: Final[str] = "Help".lower()

    _EMPTY_DEFINITION = "Definitions missing for Attribute '{}'."
    _MISSING_SPEC_DEFAULT = "Missing '{}' specification for Attribute '{}' - assuming {}."
    _MISSING_TYPE = "'AttributeType' not declare for Attribute '{}'."
    _INVALID_TYPE = "'{}' is not a valid type for an Attribute."
    _DEFAULT_NOT_LIST = "Attribute is list, but provided Default '{}' is not a list."
    _INCOMPATIBLE = "Value '{}' in section '{}' can not be converted to AttributeType '{}'."
    _DEFAULT_DISALLOWED = "Default '{}' is not an allowed value."
    _SERIES_LIST_DISALLOWED = "Attribute '{}' of type TIME_SERIES cannot be a list."
    _VALUES_ILL_FORMAT = "Only List and Dictionary is supported for 'Values' but was: {}"
    _NAME_DISALLOWED = f"Attribute name must not be empty and none of: {_DISALLOWED_NAMES}"

    def __init__(self, name: str, definition: dict):
        """Loads Attribute from given `definition`"""
        super().__init__(definition)
        self._assert_is_allowed_name(name)
        self._full_name = name

        if not definition:
            raise SchemaError(AttributeSpecs._EMPTY_DEFINITION.format(name))
        definition = keys_to_lower(definition)

        self._is_mandatory = self._get_is_mandatory(definition, name)
        self._is_list = self._get_is_list(definition, name)
        self._attr_type = self._get_type(definition, name)

        if self._attr_type == AttributeType.TIME_SERIES and self._is_list:
            raise SchemaError(AttributeSpecs._SERIES_LIST_DISALLOWED.format(name))

        self._allowed_values = self._get_allowed_values(definition)
        self._default_value = self._get_default_value(definition)
        self._nested_attributes = self._get_nested_attributes(definition, name)
        self._help = self._get_help(definition)

    @staticmethod
    def _assert_is_allowed_name(full_name: str) -> None:
        """Raises SchemaError if provided name is not allowed for Attributes"""
        if full_name is None:
            raise SchemaError(AttributeSpecs._NAME_DISALLOWED)
        short_name = full_name.split(AttributeSpecs._SEPARATOR)[-1]
        if len(short_name) == 0 or short_name.isspace():
            raise SchemaError(AttributeSpecs._NAME_DISALLOWED)
        if short_name.lower() in AttributeSpecs._DISALLOWED_NAMES:
            raise SchemaError(AttributeSpecs._NAME_DISALLOWED)

    @staticmethod
    def _get_is_mandatory(definition: dict, name: str) -> bool:
        """Returns True if `Mandatory` is set to True or if specification is missing; False otherwise"""
        if AttributeSpecs.KEY_MANDATORY in definition:
            return definition[AttributeSpecs.KEY_MANDATORY]
        log().warning(AttributeSpecs._MISSING_SPEC_DEFAULT.format(AttributeSpecs.KEY_MANDATORY, name, True))
        return True

    @staticmethod
    def _get_is_list(definition: dict, name: str) -> bool:
        """Returns True if `List` is set to True; Returns False otherwise or if specification is missing"""
        if AttributeSpecs.KEY_LIST in definition:
            return definition[AttributeSpecs.KEY_LIST]
        log().warning(AttributeSpecs._MISSING_SPEC_DEFAULT.format(AttributeSpecs.KEY_LIST, name, False))
        return False

    @staticmethod
    def _get_type(definition: dict, name: str) -> AttributeType:
        """Returns `AttributeType` from given definition; Raises an exception if no proper type can be extracted"""
        if AttributeSpecs.KEY_TYPE in definition:
            type_name = definition[AttributeSpecs.KEY_TYPE]
            try:
                return AttributeType[type_name.upper()]
            except KeyError as e:
                raise SchemaError(AttributeSpecs._INVALID_TYPE.format(type_name)) from e
        raise log_error(SchemaError(AttributeSpecs._MISSING_TYPE.format(name)))

    def _get_allowed_values(self, definition: dict) -> ValueContainer:
        """Returns ValueContainer with allowed values if defined; otherwise an empty ValueContainer"""
        allowed_values: ValueContainer = ValueContainer()
        if AttributeSpecs.KEY_VALUES in definition:
            value_definition = definition[AttributeSpecs.KEY_VALUES]
            if value_definition:
                allowed_values = self._read_values(value_definition)
        return allowed_values

    def _read_values(self, definition: [dict, list]) -> ValueContainer:
        """
        Returns accepted values mapped to their additional metadata specifications extracted from given `definition`
        Accepts lists of accepted values or dictionaries with (optional) metadata assigned to each value

        Args:
            definition: list of acceptable values or dict with acceptable values as keys and (optional) metadata content

        Returns:
            Mapping of acceptable values to their associated Metadata
        """
        try:
            value_container = ValueContainer(definition)
            for value in value_container.as_list():
                self._convert_to_data_type(value, self.KEY_VALUES)
            return value_container
        except ValueContainer.ParseError as e:
            raise SchemaError(AttributeSpecs._VALUES_ILL_FORMAT.format(definition)) from e

    def _convert_to_data_type(self, value: str, section: str) -> Union[int, float, str]:
        """Returns a given single `value` in `section` converted to this Attribute's data type"""
        try:
            return self._attr_type.convert_string_to_type(value)
        except ValueError as e:
            raise SchemaError(AttributeSpecs._INCOMPATIBLE.format(value, section, self._attr_type)) from e

    def _get_default_value(self, definition: dict) -> Optional[Union[int, float, str, list]]:
        """Returns default value(s) from given definitions, or None if no default is specified"""
        if AttributeSpecs.KEY_DEFAULT in definition:
            provided_value = definition[AttributeSpecs.KEY_DEFAULT]
            if self._is_list:
                return self._convert_list(provided_value)
            return self._convert_and_test(provided_value)
        return None

    def _convert_list(self, values) -> list:
        """Converts all entries in given `values` list to this attribute data type and returns this new list"""
        if isinstance(values, list):
            return [self._convert_and_test(item) for item in values]
        raise SchemaError(AttributeSpecs._DEFAULT_NOT_LIST.format(values))

    def _convert_and_test(self, value: str):
        """Converts a given single `value` to this Attribute's data type and tests if the value is allowed"""
        if self.has_value_restrictions and (not self._allowed_values.has_value(value)):
            raise SchemaError(AttributeSpecs._DEFAULT_DISALLOWED.format(value))
        return self._convert_to_data_type(value, self.KEY_DEFAULT)

    @staticmethod
    def _get_nested_attributes(definition: dict, name: str) -> dict[str, AttributeSpecs]:
        """Returns dict of nested attributes read from given definition; empty dict if no nested attributes exist"""
        nested_attributes = {}
        if AttributeSpecs.KEY_NESTED in definition:
            for nested_name, nested_details in definition[AttributeSpecs.KEY_NESTED].items():
                full_name = name + AttributeSpecs._SEPARATOR + nested_name
                nested_attributes[nested_name] = AttributeSpecs(full_name, nested_details)
        return nested_attributes

    @staticmethod
    def _get_help(definition) -> str:
        """Returns (possible empty) help text if provided in definition; None otherwise"""
        return definition.get(AttributeSpecs.KEY_HELP, "").strip()

    @property
    def attr_type(self) -> AttributeType:
        """Returns AttributeType of this attribute"""
        return self._attr_type

    @property
    def values(self) -> list:
        """Returns the list of allowed values for this attribute"""
        return self._allowed_values.as_list()

    @property
    def has_value_restrictions(self) -> bool:
        """Returns True if the attribute can only take a set of certain values"""
        return not self._allowed_values.is_empty()

    @property
    def is_list(self) -> bool:
        """Return True if this attribute type is a list"""
        return self._is_list

    @property
    def has_nested_attributes(self) -> bool:
        """Returns True if nested attributes are defined"""
        return bool(self._nested_attributes)

    @property
    def nested_attributes(self) -> dict[str, AttributeSpecs]:
        """Returns list of nested Attributes of this Attribute or an empty dict if no nested attributes are defined"""
        return self._nested_attributes

    @property
    def has_default_value(self) -> bool:
        """Return True if a default value is available"""
        return self._default_value is not None

    @property
    def default_value(self) -> Optional[Any]:
        """Return the default value of this attribute, or None if no default is specified"""
        return self._default_value

    @property
    def is_mandatory(self) -> bool:
        """Return True if this attribute is mandatory"""
        return self._is_mandatory

    @property
    def full_name(self) -> str:
        """Returns name including name of enclosing parent attributes"""
        return self._full_name

    @property
    def has_help_text(self) -> bool:
        """Return True if a help_text is available"""
        return bool(self._help)

    @property
    def help_text(self) -> str:
        """Return the help_text of this attribute, if any"""
        return self._help

    def _to_dict(self) -> dict[str, Any]:
        definition = {
            self.KEY_TYPE: self._attr_type.name,
            self.KEY_MANDATORY: self._is_mandatory,
            self.KEY_LIST: self._is_list,
        }
        if self.has_help_text:
            definition[self.KEY_HELP] = self._help
        if self.has_default_value:
            definition[self.KEY_DEFAULT] = self._default_value
        if self.has_value_restrictions:
            definition[self.KEY_VALUES] = self._allowed_values.to_dict()
        if self.has_nested_attributes:
            definition[self.KEY_NESTED] = {name: inner.to_dict() for name, inner in self.nested_attributes.items()}
        return definition
