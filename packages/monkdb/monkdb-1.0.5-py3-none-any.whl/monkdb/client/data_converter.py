# -*- coding: utf-8; -*-
#
# Licensed to MonkDB Labs Private Limited (MonkDB) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  MonkDB licenses
# this file to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.


import datetime as dt
import ipaddress
from copy import deepcopy
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# Type aliases for better readability
ConverterFunction = Callable[[Optional[Any]], Optional[Any]]
ColTypesDefinition = Union[int, List[Union[int, "ColTypesDefinition"]]]


def _to_ipaddress(
    value: Optional[str],
) -> Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
    """
    Converts a string representation of an IP address into an `ipaddress.IPv4Address`
    or `ipaddress.IPv6Address` object.

    Args:
        value (Optional[str]): The IP address as a string.

    Returns:
        Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]: 
        The corresponding IPv4/IPv6 object, or None if input is None.

    Example:
        >>> _to_ipaddress("192.168.1.1")
        IPv4Address('192.168.1.1')

        >>> _to_ipaddress(None)
        None
    """
    if value is None:
        return None
    return ipaddress.ip_address(value)


def _to_timestamp(value: Optional[float]) -> Optional[dt.datetime]:
    """
    Converts a timestamp (in milliseconds) to a UTC-aware `datetime` object.

    Args:
        value (Optional[float]): The timestamp in milliseconds.

    Returns:
        Optional[dt.datetime]: A UTC `datetime` object or None if input is None.

    Example:
        >>> _to_timestamp(1700000000000)
        datetime.datetime(2023, 11, 14, 23, 20, 0, tzinfo=datetime.timezone.utc)

        >>> _to_timestamp(None)
        None
    """
    if value is None:
        return None
    return dt.datetime.fromtimestamp(value / 1e3, tz=dt.timezone.utc)


def _to_default(value: Optional[Any]) -> Optional[Any]:
    """
    Default converter function that returns the input value unchanged.

    Args:
        value (Optional[Any]): The input value.

    Returns:
        Optional[Any]: The same value as input.
    """
    return value


class DataType(Enum):
    """
    Enumeration of data type identifiers used in the MonkDB HTTP interface.

    Each value corresponds to a specific data type that MonkDB supports.
    """
    NULL = 0
    NOT_SUPPORTED = 1
    CHAR = 2
    BOOLEAN = 3
    TEXT = 4
    IP = 5
    DOUBLE = 6
    REAL = 7
    SMALLINT = 8
    INTEGER = 9
    BIGINT = 10
    TIMESTAMP_WITH_TZ = 11
    OBJECT = 12
    GEOPOINT = 13
    GEOSHAPE = 14
    TIMESTAMP_WITHOUT_TZ = 15
    UNCHECKED_OBJECT = 16
    REGPROC = 19
    TIME = 20
    OIDVECTOR = 21
    NUMERIC = 22
    REGCLASS = 23
    DATE = 24
    BIT = 25
    JSON = 26
    CHARACTER = 27
    ARRAY = 100


# Type alias for mapping data types to conversion functions
ConverterMapping = Dict[DataType, ConverterFunction]

# Default converters for specific data types
_DEFAULT_CONVERTERS: ConverterMapping = {
    DataType.IP: _to_ipaddress,
    DataType.TIMESTAMP_WITH_TZ: _to_timestamp,
    DataType.TIMESTAMP_WITHOUT_TZ: _to_timestamp,
}


class MonkConverter:
    """
    A class that maps MonkDB data types to their corresponding conversion functions.

    Allows retrieving and setting custom converter functions.

    Attributes:
        _mappings (ConverterMapping): A dictionary mapping `DataType` to `ConverterFunction`.
        _default (ConverterFunction): The default converter function when no specific mapping exists.
    """

    def __init__(
        self,
        mappings: Optional[ConverterMapping] = None,
        default: ConverterFunction = _to_default,
    ) -> None:
        """
        Initializes a `MonkConverter` with custom or default mappings.

        Args:
            mappings (Optional[ConverterMapping]): A dictionary mapping `DataType` to custom `ConverterFunction`.
            default (ConverterFunction): The default conversion function for unknown types.
        """
        self._mappings = mappings or {}
        self._default = default

    def get(self, type_: ColTypesDefinition) -> ConverterFunction:
        """
        Retrieves the appropriate converter function for a given data type.

        Args:
            type_ (ColTypesDefinition): The MonkDB data type (either an integer or an array structure).

        Returns:
            ConverterFunction: The corresponding converter function.

        Raises:
            ValueError: If a non-array type is incorrectly used as a collection.
        """
        if isinstance(type_, int):
            return self._mappings.get(DataType(type_), self._default)

        type_, inner_type = type_
        if DataType(type_) is not DataType.ARRAY:
            raise ValueError(
                f"Data type {type_} is not implemented as a collection type"
            )

        inner_convert = self.get(inner_type)

        def convert(value: Any) -> Optional[List[Any]]:
            """
            Converts an array of values using the inner type's converter function.

            Args:
                value (Any): The input value.

            Returns:
                Optional[List[Any]]: A list of converted values or None.
            """
            if value is None:
                return None
            return [inner_convert(x) for x in value]

        return convert

    def set(self, type_: DataType, converter: ConverterFunction):
        """
        Sets a custom converter function for a specific data type.

        Args:
            type_ (DataType): The MonkDB data type.
            converter (ConverterFunction): The conversion function to associate with the data type.
        """
        self._mappings[type_] = converter


class MonkDefaultTypeConverter(MonkConverter):
    """
    A `MonkConverter` with built-in default mappings for MonkDB data types.

    Attributes:
        _mappings (ConverterMapping): A dictionary mapping `DataType` to converter functions.
    """

    def __init__(
        self, more_mappings: Optional[ConverterMapping] = None
    ) -> None:
        """
        Initializes a `MonkDefaultTypeConverter` with default and additional mappings.

        Args:
            more_mappings (Optional[ConverterMapping]): Additional mappings to extend default converters.
        """
        mappings: ConverterMapping = {}
        mappings.update(deepcopy(_DEFAULT_CONVERTERS))
        if more_mappings:
            mappings.update(deepcopy(more_mappings))
        super().__init__(mappings=mappings, default=_to_default)
