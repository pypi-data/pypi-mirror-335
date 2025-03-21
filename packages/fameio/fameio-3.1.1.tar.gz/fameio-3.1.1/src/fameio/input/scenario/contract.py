# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any, Optional, Final

from fameio.input.metadata import Metadata
from fameio.logs import log
from fameio.time import FameTime
from fameio.tools import ensure_is_list, keys_to_lower
from .attribute import Attribute
from .exception import get_or_default, get_or_raise, log_and_raise


class Contract(Metadata):
    """Contract between two Agents of a scenario"""

    KEY_SENDER: Final[str] = "SenderId".lower()
    KEY_RECEIVER: Final[str] = "ReceiverId".lower()
    KEY_PRODUCT: Final[str] = "ProductName".lower()
    KEY_FIRST_DELIVERY: Final[str] = "FirstDeliveryTime".lower()
    KEY_INTERVAL: Final[str] = "DeliveryIntervalInSteps".lower()
    KEY_EXPIRE: Final[str] = "ExpirationTime".lower()
    KEY_ATTRIBUTES: Final[str] = "Attributes".lower()

    _ERR_MISSING_KEY = "Contract requires key '{}' but is missing it."
    _ERR_MULTI_CONTRACT_CORRUPT = (
        "Definition of Contracts is valid only for One-to-One, One-to-many, Many-to-one, "
        "or N-to-N sender-to-receiver numbers. Found M-to-N pairing in Contract with "
        "Senders: {} and Receivers: {}."
    )
    _ERR_INTERVAL_NOT_POSITIVE = "Contract delivery interval must be a positive integer but was: {}"
    _ERR_SENDER_IS_RECEIVER = "Contract sender and receiver have the same id: {}"
    _ERR_DOUBLE_ATTRIBUTE = "Cannot add attribute '{}' to contract because it already exists."

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        sender_id: int,
        receiver_id: int,
        product_name: str,
        delivery_interval: int,
        first_delivery_time: int,
        expiration_time: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Constructs a new Contract"""
        super().__init__({self.KEY_METADATA: metadata} if metadata else None)
        assert product_name != ""
        if sender_id == receiver_id:
            log().warning(self._ERR_SENDER_IS_RECEIVER.format(sender_id))
        if delivery_interval <= 0:
            raise ValueError(self._ERR_INTERVAL_NOT_POSITIVE.format(delivery_interval))
        self._sender_id = sender_id
        self._receiver_id = receiver_id
        self._product_name = product_name
        self._delivery_interval = delivery_interval
        self._first_delivery_time = first_delivery_time
        self._expiration_time = expiration_time
        self._attributes = {}

    def _notify_data_changed(self):
        """Placeholder method used to signal data changes to derived types"""

    @property
    def product_name(self) -> str:
        """Returns the product name of the contract"""
        return self._product_name

    @property
    def sender_id(self) -> int:
        """Returns the sender ID of the contract"""
        return self._sender_id

    @property
    def display_sender_id(self) -> str:
        """Returns the sender ID of the contract as a string for display purposes"""
        return f"#{self._sender_id}"

    @property
    def receiver_id(self) -> int:
        """Returns the receiver ID of the contract"""
        return self._receiver_id

    @property
    def display_receiver_id(self) -> str:
        """Returns the receiver ID of the contract as a string for display purposes"""
        return f"#{self._receiver_id}"

    @property
    def delivery_interval(self) -> int:
        """Returns the delivery interval of the contract (in steps)"""
        return self._delivery_interval

    @property
    def first_delivery_time(self) -> int:
        """Returns the first delivery time of the contract"""
        return self._first_delivery_time

    @property
    def expiration_time(self) -> Optional[int]:
        """Returns the expiration time of the contract if available, None otherwise"""
        return self._expiration_time

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Returns dictionary of all Attributes of the contract"""
        return self._attributes

    def add_attribute(self, name: str, value: Attribute) -> None:
        """Adds a new attribute to the Contract (raise an error if it already exists)"""
        if name in self._attributes:
            raise ValueError(self._ERR_DOUBLE_ATTRIBUTE.format(name))
        self._attributes[name] = value
        self._notify_data_changed()

    @classmethod
    def from_dict(cls, definitions: dict) -> Contract:
        """Parses Contract from given `definitions`"""
        definitions = keys_to_lower(definitions)
        sender_id = get_or_raise(definitions, Contract.KEY_SENDER, Contract._ERR_MISSING_KEY)
        receiver_id = get_or_raise(definitions, Contract.KEY_RECEIVER, Contract._ERR_MISSING_KEY)
        product_name = get_or_raise(definitions, Contract.KEY_PRODUCT, Contract._ERR_MISSING_KEY)
        first_delivery_time = FameTime.convert_string_if_is_datetime(
            get_or_raise(definitions, Contract.KEY_FIRST_DELIVERY, Contract._ERR_MISSING_KEY)
        )
        delivery_interval = get_or_raise(definitions, Contract.KEY_INTERVAL, Contract._ERR_MISSING_KEY)
        expiration_time = get_or_default(definitions, Contract.KEY_EXPIRE, None)
        expiration_time = FameTime.convert_string_if_is_datetime(expiration_time) if expiration_time else None

        contract = cls(
            sender_id,
            receiver_id,
            product_name,
            delivery_interval,
            first_delivery_time,
            expiration_time,
        )
        contract._extract_metadata(definitions)
        attribute_definitions = get_or_default(definitions, Contract.KEY_ATTRIBUTES, {})
        contract._init_attributes_from_dict(attribute_definitions)
        return contract

    def _init_attributes_from_dict(self, attributes: dict[str, Any]) -> None:
        """Resets Contract `attributes` from dict; Must only be called when creating a new Contract"""
        assert len(self._attributes) == 0
        self._attributes = {}
        for name, value in attributes.items():
            full_name = f"{type}.{id}{name}"
            self.add_attribute(name, Attribute(full_name, value))

    def _to_dict(self) -> dict:
        """Serializes the Contract content to a dict"""
        result = {
            self.KEY_SENDER: self.sender_id,
            self.KEY_RECEIVER: self.receiver_id,
            self.KEY_PRODUCT: self.product_name,
            self.KEY_FIRST_DELIVERY: self.first_delivery_time,
            self.KEY_INTERVAL: self.delivery_interval,
        }

        if self.expiration_time is not None:
            result[self.KEY_EXPIRE] = self.expiration_time

        if len(self.attributes) > 0:
            result[self.KEY_ATTRIBUTES] = {name: value.to_dict() for name, value in self.attributes.items()}
        return result

    @staticmethod
    def split_contract_definitions(multi_definition: dict) -> list[dict]:
        """Splits given `multi_definition` dictionary into list of individual Contract definitions"""
        contracts = []
        base_data = {}
        multi_definition = keys_to_lower(multi_definition)
        for key in [
            Contract.KEY_PRODUCT,
            Contract.KEY_FIRST_DELIVERY,
            Contract.KEY_INTERVAL,
            Contract.KEY_EXPIRE,
            Contract.KEY_METADATA,
            Contract.KEY_ATTRIBUTES,
        ]:
            if key in multi_definition:
                base_data[key] = multi_definition[key]
        senders = ensure_is_list(get_or_raise(multi_definition, Contract.KEY_SENDER, Contract._ERR_MISSING_KEY))
        receivers = ensure_is_list(get_or_raise(multi_definition, Contract.KEY_RECEIVER, Contract._ERR_MISSING_KEY))
        if len(senders) > 1 and len(receivers) == 1:
            for index, sender in enumerate(senders):
                contracts.append(Contract._copy_contract(sender, receivers[0], base_data))
        elif len(senders) == 1 and len(receivers) > 1:
            for index, receiver in enumerate(receivers):
                contracts.append(Contract._copy_contract(senders[0], receiver, base_data))
        elif len(senders) == len(receivers):
            for index in range(len(senders)):  # pylint: disable=consider-using-enumerate
                contracts.append(Contract._copy_contract(senders[index], receivers[index], base_data))
        else:
            log_and_raise(Contract._ERR_MULTI_CONTRACT_CORRUPT.format(senders, receivers))
        return contracts

    @staticmethod
    def _copy_contract(sender: int, receiver: int, base_data: dict) -> dict:
        """Returns a new contract definition dictionary, with given `sender` and `receiver` and copied `base_data`"""
        contract = {
            Contract.KEY_SENDER: sender,
            Contract.KEY_RECEIVER: receiver,
        }
        contract.update(base_data)
        return contract
