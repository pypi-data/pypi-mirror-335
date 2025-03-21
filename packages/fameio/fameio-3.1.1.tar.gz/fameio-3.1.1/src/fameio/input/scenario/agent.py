# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import ast
from typing import Any, Final

from fameio.input.metadata import Metadata
from fameio.tools import keys_to_lower
from .attribute import Attribute
from .exception import assert_or_raise, get_or_default, get_or_raise


class Agent(Metadata):
    """Contains specifications for an agent in a scenario"""

    KEY_TYPE: Final[str] = "Type".lower()
    KEY_ID: Final[str] = "Id".lower()
    KEY_ATTRIBUTES: Final[str] = "Attributes".lower()

    _ERR_MISSING_KEY = "Agent requires `key` '{}' but is missing it."
    _ERR_MISSING_TYPE = "Agent requires `type` but is missing it."
    _ERR_MISSING_ID = "Agent requires a positive integer `id` but was '{}'."
    _ERR_DOUBLE_ATTRIBUTE = "Cannot add attribute '{}' to agent {} because it already exists."
    _ERR_ATTRIBUTE_OVERWRITE = "Agent's attributes are already set and would be overwritten."

    def __init__(self, agent_id: int, type_name: str, metadata: dict = None) -> None:
        """Constructs a new Agent"""
        super().__init__({Agent.KEY_METADATA: metadata} if metadata else None)
        assert_or_raise(isinstance(agent_id, int) and agent_id >= 0, self._ERR_MISSING_ID.format(agent_id))
        assert_or_raise(bool(type_name and type_name.strip()), self._ERR_MISSING_TYPE)
        self._id: int = agent_id
        self._type_name: str = type_name.strip()
        self._attributes: dict[str, Attribute] = {}

    @classmethod
    def from_dict(cls, definitions: dict) -> Agent:
        """Parses an agent from provided `definitions`"""
        definitions = keys_to_lower(definitions)
        agent_type = get_or_raise(definitions, Agent.KEY_TYPE, Agent._ERR_MISSING_TYPE)
        agent_id = get_or_raise(definitions, Agent.KEY_ID, Agent._ERR_MISSING_ID)
        agent = cls(agent_id, agent_type)
        agent._extract_metadata(definitions)
        attribute_definitions = get_or_default(definitions, Agent.KEY_ATTRIBUTES, {})
        agent.init_attributes_from_dict(attribute_definitions)
        agent._meta_data = get_or_default(definitions, Agent.KEY_METADATA, {})
        return agent

    def init_attributes_from_dict(self, attributes: dict[str, Any]) -> None:
        """Initialize Agent `attributes` from dict; Must only be called when creating a new Agent"""
        assert_or_raise(not self._attributes, self._ERR_ATTRIBUTE_OVERWRITE)
        self._attributes = {}
        for name, value in attributes.items():
            full_name = f"{self.type_name}({self.id}): {name}"
            self.add_attribute(name, Attribute(full_name, value))

    def add_attribute(self, name: str, value: Attribute) -> None:
        """Adds a new attribute to the Agent (raise an error if it already exists)"""
        if name in self._attributes:
            raise ValueError(self._ERR_DOUBLE_ATTRIBUTE.format(name, self.display_id))
        self._attributes[name] = value
        self._notify_data_changed()

    def _to_dict(self) -> dict:
        """Serializes the Agent's content to a dict"""
        result = {Agent.KEY_TYPE: self.type_name, Agent.KEY_ID: self.id}
        if self._attributes:
            result[self.KEY_ATTRIBUTES] = {name: value.to_dict() for name, value in self._attributes.items()}
        return result

    def to_string(self) -> str:
        """Serializes this agent to a string"""
        return repr(self.to_dict())

    @classmethod
    def from_string(cls, definitions: str) -> Agent:
        return cls.from_dict(ast.literal_eval(definitions))

    def _notify_data_changed(self):
        """Placeholder method used to signal data changes to derived types"""

    @property
    def id(self) -> int:
        """Returns the ID of the Agent"""
        return self._id

    @property
    def display_id(self) -> str:
        """Returns the ID of the Agent as a string for display purposes"""
        return f"#{self._id}"

    @property
    def type_name(self) -> str:
        """Returns the name of the Agent type"""
        return self._type_name

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Returns dictionary of all Attributes of this agent"""
        return self._attributes
