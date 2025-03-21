# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Union

from fameprotobuf.services_pb2 import Output


class AgentType:
    """Provides information derived from an underlying protobuf AgentType"""

    def __init__(self, agent_type: Output.AgentType) -> None:
        self._agent_type = agent_type

    def get_simple_column_map(self) -> dict[int, str]:
        """Returns dictionary of simple column IDs mapped to their name - ignoring complex columns"""
        return {field.field_id: field.field_name for field in self._agent_type.fields if len(field.index_names) == 0}

    def get_merged_column_map(self) -> dict[int, str]:
        """Returns dictionary of all column IDs mapped to their name merged with names of inner complex columns"""
        column_names = {}
        for field in self._agent_type.fields:
            if len(field.index_names) == 0:
                column_names[field.field_id] = field.field_name
            else:
                column_names[field.field_id] = f"{field.field_name}_({tuple(field.index_names)}, value)"
        return column_names

    def get_simple_column_mask(self) -> list[bool]:
        """Returns list of bool - where an entry is True if the output column with the same index is not complex"""
        return [len(field.index_names) == 0 for field in self._agent_type.fields]

    def get_complex_column_ids(self) -> set[int]:
        """Returns set of IDs for complex columns, ignoring simple columns"""
        return {field.field_id for field in self._agent_type.fields if len(field.index_names) > 0}

    def get_column_name_for_id(self, column_index: int) -> Union[str, None]:
        """Returns name of column by given `column_index` or None, if column is not present"""
        if 0 <= column_index < len(self._agent_type.fields):
            return self._agent_type.fields[column_index].field_name
        return None

    def get_inner_columns(self, column_index: int) -> tuple[str, ...]:
        """Returns tuple of inner column names for complex column with given `column_index`"""
        return tuple(self._agent_type.fields[column_index].index_names)

    def get_class_name(self) -> str:
        """Returns name of class of wrapped agent type"""
        return self._agent_type.class_name


class AgentTypeError(Exception):
    """Indicates an error with the agent types definitions"""


class AgentTypeLog:
    """Stores data about collected agent types"""

    _ERR_AGENT_TYPE_MISSING = "Requested AgentType `{}` not found."
    _ERR_DOUBLE_DEFINITION = "Just one definition allowed per AgentType. Found multiple for {}. File might be corrupt."

    def __init__(self, requested_agents: list[str]) -> None:
        self._requested_agents = [agent.upper() for agent in requested_agents] if requested_agents else None
        self._requested_agent_types = {}

    def update_agents(self, new_types: dict[str, Output.AgentType]) -> None:
        """Saves new `agent_types` (if any) contained in given `output` if requested for extraction"""
        if new_types:
            if self._requested_agents:
                new_types = {
                    agent_name: agent_type
                    for agent_name, agent_type in new_types.items()
                    if agent_name.upper() in self._requested_agents
                }
            for agent_name in self._requested_agent_types:
                if agent_name in new_types:
                    raise AgentTypeError(self._ERR_DOUBLE_DEFINITION.format(agent_name))
            self._requested_agent_types.update(new_types)

    def has_any_agent_type(self) -> bool:
        """Returns True if any agent type was registered so far present"""
        return len(self._requested_agent_types) > 0

    def get_agent_type(self, agent_name: str) -> AgentType:
        """Returns `AgentType` of given agent `name`"""
        if agent_name not in self._requested_agent_types:
            raise AgentTypeError(self._ERR_AGENT_TYPE_MISSING.format(agent_name))
        return AgentType(self._requested_agent_types[agent_name])

    def is_requested(self, agent_name: str) -> bool:
        """Returns True if given agent_name is known and requested"""
        return agent_name in self._requested_agent_types
