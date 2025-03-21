# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import math
from collections import Counter
from typing import Any, Union

from fameio.input.resolver import PathResolver
from fameio.input.scenario import Agent, Attribute, Contract, Scenario, StringSet
from fameio.input.schema import Schema, AttributeSpecs, AttributeType, AgentType
from fameio.logs import log, log_error
from fameio.series import TimeSeriesManager, TimeSeriesError
from fameio.time import FameTime


class ValidationError(Exception):
    """Indicates an error occurred during validation of any data with a connected schema"""


class SchemaValidator:
    """Handles validation of scenarios based on a connected `schema`"""

    _AGENT_ID_NOT_UNIQUE = "Agent ID(s) not unique: '{}'."
    _AGENT_TYPE_UNKNOWN = "Agent type '{}' not declared in Schema."
    _ATTRIBUTE_UNKNOWN = "Attribute '{}' not declared in Schema."
    _TYPE_NOT_IMPLEMENTED = "Validation not implemented for AttributeType '{}'."
    _INCOMPATIBLE = "Value '{}' incompatible with {} of Attribute '{}'."
    _DISALLOWED = "Value '{}' not in list of allowed values of Attribute '{}'"
    _AGENT_MISSING = "Contract mentions Agent with ID '{}' but Agent was not declared."
    _PRODUCT_MISSING = "Product '{}' not declared in Schema for AgentType '{}'."
    _KEY_MISSING = "Required key '{}' missing in dictionary '{}'."
    _ATTRIBUTE_MISSING = "Mandatory attribute '{}' is missing."
    _DEFAULT_IGNORED = "Optional Attribute: '{}': not specified - provided Default ignored for optional Attributes."
    _OPTIONAL_MISSING = "Optional Attribute: '{}': not specified."
    _IS_NO_LIST = "Attribute '{}' is list but assigned value '{}' is not a list."
    _TIME_SERIES_INVALID = "Timeseries at '{}' is invalid."
    _MISSING_CONTRACTS_FOR_AGENTS = "No contracts defined for Agent '{}' of type '{}'"
    _MISSING_STRING_SET = "StringSet '{}' not defined in scenario."
    _MISSING_STRING_SET_ENTRY = "Value '{}' of Attribute '{}' not defined in StringSet '{}'"

    @staticmethod
    def validate_scenario_and_timeseries(
        scenario: Scenario, path_resolver: PathResolver = PathResolver()
    ) -> TimeSeriesManager:
        """
        Validates the given `scenario` and its timeseries using given `path_resolver`
        Raises an exception if schema requirements are not met or timeseries data are erroneous.

        Args:
            scenario: to be validated against the encompassed schema
            path_resolver: to resolve paths of timeseries

        Returns:
            a new TimeSeriesManager initialised with validated time series from scenario
        Raises:
            ValidationException: if an error in the scenario or in timeseries is spotted
        """
        schema = scenario.schema
        agents = scenario.agents
        timeseries_manager = TimeSeriesManager(path_resolver)

        SchemaValidator.ensure_unique_agent_ids(agents)
        for agent in agents:
            SchemaValidator.ensure_agent_and_timeseries_are_valid(agent, schema, timeseries_manager)
            SchemaValidator.ensure_string_set_consistency(agent, schema, scenario.string_sets)

        agent_types_by_id = {agent.id: agent.type_name for agent in agents}
        for contract in scenario.contracts:
            SchemaValidator.ensure_is_valid_contract(contract, schema, agent_types_by_id)

        return timeseries_manager

    @staticmethod
    def ensure_unique_agent_ids(agents: list[Agent]) -> None:
        """Raises exception if any id for given `agents` is not unique"""
        list_of_ids = [agent.id for agent in agents]
        non_unique_ids = [agent_id for agent_id, count in Counter(list_of_ids).items() if count > 1]
        if non_unique_ids:
            raise log_error(ValidationError(SchemaValidator._AGENT_ID_NOT_UNIQUE.format(non_unique_ids)))

    @staticmethod
    def ensure_agent_and_timeseries_are_valid(agent: Agent, schema: Schema, timeseries_manager: TimeSeriesManager):
        """Validates given `agent` against `schema` plus loads and validates its timeseries"""
        SchemaValidator.ensure_agent_type_in_schema(agent, schema)
        SchemaValidator.ensure_is_valid_agent(agent, schema, timeseries_manager)
        SchemaValidator.load_and_validate_timeseries(agent, schema, timeseries_manager)

    @staticmethod
    def ensure_agent_type_in_schema(agent: Agent, schema: Schema) -> None:
        """Raises exception if type for given `agent` is not specified in given `schema`"""
        if agent.type_name not in schema.agent_types:
            raise log_error(ValidationError(SchemaValidator._AGENT_TYPE_UNKNOWN.format(agent.type_name)))

    @staticmethod
    def ensure_is_valid_agent(agent: Agent, schema: Schema, timeseries_manager: TimeSeriesManager) -> None:
        """Raises an exception if given `agent` does not meet the specified `schema` requirements"""
        scenario_attributes = agent.attributes
        schema_attributes = SchemaValidator._get_agent(schema, agent.type_name).attributes
        missing_default_series = SchemaValidator._check_mandatory_or_default(scenario_attributes, schema_attributes)
        for missing_series in missing_default_series:
            timeseries_manager.register_and_validate(missing_series)
        SchemaValidator._ensure_attributes_exist(scenario_attributes, schema_attributes)
        SchemaValidator._ensure_value_and_type_match(scenario_attributes, schema_attributes)

    @staticmethod
    def _get_agent(schema: Schema, name: str) -> AgentType:
        """Returns agent specified by `name` or raises Exception if this agent is not present in given `schema`"""
        if name in schema.agent_types:
            return schema.agent_types[name]
        raise log_error(ValidationError(SchemaValidator._AGENT_TYPE_UNKNOWN.format(name)))

    @staticmethod
    def _check_mandatory_or_default(
        attributes: dict[str, Attribute],
        specifications: dict[str, AttributeSpecs],
    ) -> list[Union[str, float]]:
        """
        Raises Exception if in given list of `specifications` at least one item is mandatory,
        provides no defaults and is not contained in given `attributes` dictionary

        Returns:
            list of time series defaults used in scenario
        """
        missing_series_defaults = []
        for name, specification in specifications.items():
            if name not in attributes:
                if specification.is_mandatory:
                    if not specification.has_default_value:
                        raise log_error(
                            ValidationError(SchemaValidator._ATTRIBUTE_MISSING.format(specification.full_name))
                        )
                    if specification.attr_type == AttributeType.TIME_SERIES:
                        missing_series_defaults.append(specification.default_value)
                else:
                    if specification.has_default_value:
                        log().warning(SchemaValidator._DEFAULT_IGNORED.format(specification.full_name))
                    else:
                        log().info(SchemaValidator._OPTIONAL_MISSING.format(specification.full_name))
            if name in attributes and specification.has_nested_attributes:
                attribute = attributes[name]
                if specification.is_list:
                    for entry in attribute.nested_list:
                        missing_series_defaults.extend(
                            SchemaValidator._check_mandatory_or_default(entry, specification.nested_attributes)
                        )
                else:
                    missing_series_defaults.extend(
                        SchemaValidator._check_mandatory_or_default(attribute.nested, specification.nested_attributes)
                    )
        return missing_series_defaults

    @staticmethod
    def _ensure_attributes_exist(attributes: dict[str, Attribute], specifications: dict[str, AttributeSpecs]) -> None:
        """Raises exception any entry of given `attributes` has no corresponding type `specification`"""
        for name, attribute in attributes.items():
            if name not in specifications:
                raise log_error(ValidationError(SchemaValidator._ATTRIBUTE_UNKNOWN.format(attribute)))
            if attribute.has_nested:
                specification = specifications[name]
                SchemaValidator._ensure_attributes_exist(attribute.nested, specification.nested_attributes)
            if attribute.has_nested_list:
                specification = specifications[name]
                for entry in attribute.nested_list:
                    SchemaValidator._ensure_attributes_exist(entry, specification.nested_attributes)

    @staticmethod
    def _ensure_value_and_type_match(
        attributes: dict[str, Attribute], specifications: dict[str, AttributeSpecs]
    ) -> None:
        """Raises exception if in given list of `attributes` its value does not match associated type `specification`"""
        for name, attribute in attributes.items():
            specification = specifications[name]
            if attribute.has_value:
                value = attribute.value
                type_spec = specification.attr_type
                if not SchemaValidator._is_compatible(specification, value):
                    message = SchemaValidator._INCOMPATIBLE.format(value, type_spec, specification.full_name)
                    raise log_error(ValidationError(message))
                if not SchemaValidator._is_allowed_value(specification, value):
                    message = SchemaValidator._DISALLOWED.format(value, specification.full_name)
                    raise log_error(ValidationError(message))
            if attribute.has_nested:
                SchemaValidator._ensure_value_and_type_match(attribute.nested, specification.nested_attributes)
            if attribute.has_nested_list:
                for entry in attribute.nested_list:
                    SchemaValidator._ensure_value_and_type_match(entry, specification.nested_attributes)

    @staticmethod
    def _is_compatible(specification: AttributeSpecs, value_or_values: Any) -> bool:
        """Returns True if given `value_or_values` is compatible to specified `attribute_type` and `should_be_list`"""
        is_list = isinstance(value_or_values, list)
        attribute_type = specification.attr_type
        if specification.is_list:
            if not is_list:
                log().warning(SchemaValidator._IS_NO_LIST.format(specification.full_name, value_or_values))
                return SchemaValidator._is_compatible_value(attribute_type, value_or_values)
            for value in value_or_values:
                if not SchemaValidator._is_compatible_value(attribute_type, value):
                    return False
            return True
        return (not is_list) and SchemaValidator._is_compatible_value(attribute_type, value_or_values)

    @staticmethod
    def _is_compatible_value(attribute_type: AttributeType, value) -> bool:
        """Returns True if given single value is compatible to specified `attribute_type` and is not a NaN float"""
        if attribute_type is AttributeType.INTEGER:
            if isinstance(value, int):
                return -2147483648 < value < 2147483647
            return False
        if attribute_type is AttributeType.LONG:
            return isinstance(value, int)
        if attribute_type is AttributeType.DOUBLE:
            return isinstance(value, (int, float)) and not math.isnan(value)
        if attribute_type in (AttributeType.ENUM, AttributeType.STRING, AttributeType.STRING_SET):
            return isinstance(value, str)
        if attribute_type is AttributeType.TIME_STAMP:
            return FameTime.is_fame_time_compatible(value)
        if attribute_type is AttributeType.TIME_SERIES:
            return isinstance(value, (str, int)) or (isinstance(value, float) and not math.isnan(value))
        raise log_error(ValidationError(SchemaValidator._TYPE_NOT_IMPLEMENTED.format(attribute_type)))

    @staticmethod
    def _is_allowed_value(attribute: AttributeSpecs, value) -> bool:
        """Returns True if `value` matches an entry of given `Attribute`'s value list or if this list is empty"""
        if not attribute.values:
            return True
        return value in attribute.values

    @staticmethod
    def load_and_validate_timeseries(agent: Agent, schema: Schema, timeseries_manager: TimeSeriesManager) -> None:
        """
        Loads all timeseries specified in given `schema` of given `agent` into given `timeseries_manager`

        Args:
            agent: definition in scenario
            schema: schema encompassed in scenario
            timeseries_manager: to be filled with timeseries

        Raises:
            ValidationException: if timeseries is not found, ill-formatted or invalid
        """
        scenario_attributes = agent.attributes
        schema_attributes = SchemaValidator._get_agent(schema, agent.type_name).attributes
        SchemaValidator._ensure_valid_timeseries(scenario_attributes, schema_attributes, timeseries_manager)

    @staticmethod
    def _ensure_valid_timeseries(
        attributes: dict[str, Attribute], specifications: dict[str, AttributeSpecs], manager: TimeSeriesManager
    ) -> None:
        """Recursively searches for time_series in agent attributes and registers them at given `manager`"""
        for name, attribute in attributes.items():
            specification = specifications[name]
            if attribute.has_value:
                attribute_type = specification.attr_type
                if attribute_type is AttributeType.TIME_SERIES:
                    try:
                        manager.register_and_validate(attribute.value)
                    except TimeSeriesError as e:
                        message = SchemaValidator._TIME_SERIES_INVALID.format(specification.full_name)
                        raise log_error(ValidationError(message, e)) from e
            if attribute.has_nested:
                SchemaValidator._ensure_valid_timeseries(attribute.nested, specification.nested_attributes, manager)
            if attribute.has_nested_list:
                for entry in attribute.nested_list:
                    SchemaValidator._ensure_valid_timeseries(entry, specification.nested_attributes, manager)

    @staticmethod
    def ensure_string_set_consistency(agent: Agent, schema: Schema, string_sets: dict[str, StringSet]) -> None:
        """
        Raises exception if
            a) an agent's attribute is of type StringSet but the corresponding StringSet is not defined in the scenario
            b) the value assigned to an attribute of type StringSet is not contained in the corresponding StringSet
        """
        scenario_attributes = agent.attributes
        schema_attributes = SchemaValidator._get_agent(schema, agent.type_name).attributes
        SchemaValidator._ensure_string_set_consistency(scenario_attributes, schema_attributes, string_sets)

    @staticmethod
    def _ensure_string_set_consistency(
        attributes: dict[str, Attribute], specifications: dict[str, AttributeSpecs], string_sets: dict[str, StringSet]
    ) -> None:
        """
        Recursively iterates through all attributes of an agent, applying tests if attribute type is `StringSet`
        Raises:
            ValidationException: if
                a) StringSet mentioned in schema is not defined in the scenario
                b) the value assigned to an attribute of type StringSet is not contained in the corresponding StringSet
        """
        for name, attribute in attributes.items():
            specification = specifications[name]
            if attribute.has_value:
                attribute_type = specification.attr_type
                if attribute_type is AttributeType.STRING_SET:
                    if name in string_sets:
                        if not string_sets[name].is_in_set(attribute.value):
                            msg = SchemaValidator._MISSING_STRING_SET_ENTRY.format(
                                attribute.value, str(attribute), name
                            )
                            raise log_error(ValidationError(msg))
                    else:
                        msg = SchemaValidator._MISSING_STRING_SET.format(specification.full_name)
                        raise log_error(ValidationError(msg))
            if attribute.has_nested:
                SchemaValidator._ensure_string_set_consistency(
                    attribute.nested, specification.nested_attributes, string_sets
                )
            if attribute.has_nested_list:
                for entry in attribute.nested_list:
                    SchemaValidator._ensure_string_set_consistency(entry, specification.nested_attributes, string_sets)

    @staticmethod
    def ensure_is_valid_contract(contract: Contract, schema: Schema, agent_types_by_id: dict[int, str]) -> None:
        """Raises exception if given `contract` does not meet the `schema`'s requirements, using `agent_types_by_id`"""
        sender_id = contract.sender_id
        if sender_id not in agent_types_by_id:
            raise log_error(ValidationError(SchemaValidator._AGENT_MISSING.format(sender_id)))
        if contract.receiver_id not in agent_types_by_id:
            raise log_error(ValidationError(SchemaValidator._AGENT_MISSING.format(contract.receiver_id)))
        sender_type_name = agent_types_by_id[sender_id]
        if sender_type_name not in schema.agent_types:
            raise log_error(ValidationError(SchemaValidator._AGENT_TYPE_UNKNOWN.format(sender_type_name)))
        sender_type = schema.agent_types[sender_type_name]
        product = contract.product_name
        if product not in sender_type.products:
            raise log_error(ValidationError(SchemaValidator._PRODUCT_MISSING.format(product, sender_type_name)))

    @staticmethod
    def check_agents_have_contracts(scenario: Scenario) -> None:
        """Raises warning for each agent without any assigned contract"""
        senders = [contract.sender_id for contract in scenario.contracts]
        receivers = [contract.receiver_id for contract in scenario.contracts]
        active_agents = set(senders + receivers)
        inactive_agents = {agent.id: agent.type_name for agent in scenario.agents if agent.id not in active_agents}

        if inactive_agents:
            for agent_id, agent_name in inactive_agents.items():
                log().warning(SchemaValidator._MISSING_CONTRACTS_FOR_AGENTS.format(agent_id, agent_name))
