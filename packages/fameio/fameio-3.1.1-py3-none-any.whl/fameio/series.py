# SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0
import math
import os
from enum import Enum, auto
from pathlib import Path
from typing import Union, Any

import pandas as pd
from fameprotobuf.input_file_pb2 import InputData
from google.protobuf.internal.wire_format import INT64_MIN, INT64_MAX

from fameio.input.resolver import PathResolver
from fameio.logs import log, log_error
from fameio.time import ConversionError, FameTime
from fameio.tools import clean_up_file_name


CSV_FILE_SUFFIX = ".csv"


class TimeSeriesError(Exception):
    """Indicates that an error occurred during management of time series"""


class Entry(Enum):
    ID = auto()
    NAME = auto()
    DATA = auto()


class TimeSeriesManager:
    """Manages matching of files to time series ids and their protobuf representation"""

    _TIMESERIES_RECONSTRUCTION_PATH = "./timeseries/"
    _CONSTANT_IDENTIFIER = "Constant value: {}"
    _KEY_ROW_TIME = "timeStep"
    _KEY_ROW_VALUE = "value"

    _ERR_FILE_NOT_FOUND = "Cannot find Timeseries file '{}'."
    _ERR_NUMERIC_STRING = " Remove quotes to use a constant numeric value instead of a timeseries file."
    _ERR_CORRUPT_TIME_SERIES_KEY = "TimeSeries file '{}' corrupt: At least one entry in first column isn't a timestamp."
    _ERR_CORRUPT_TIME_SERIES_VALUE = "TimeSeries file '{}' corrupt: At least one entry in value column isn't numeric."
    _ERR_NON_NUMERIC = "Values in TimeSeries must be numeric but was: '{}'"
    _ERR_NAN_VALUE = "Values in TimeSeries must not be missing or NaN."
    _ERR_UNREGISTERED_SERIES = "No timeseries registered with identifier '{}' - was the Scenario validated?"
    _WARN_NO_DATA = "No timeseries stored in timeseries manager. Double check if you expected timeseries."
    _WARN_DATA_IGNORED = "Timeseries contains additional columns with data which will be ignored."

    def __init__(self, path_resolver: PathResolver = PathResolver()) -> None:
        self._path_resolver = path_resolver
        self._id_count = -1
        self._series_by_id: dict[Union[str, int, float], dict[Entry, Any]] = {}

    def register_and_validate(self, identifier: Union[str, int, float]) -> None:
        """
        Registers given timeseries `identifier` and validates associated timeseries

        Args:
            identifier: to be registered - either a single numeric value or a string pointing to a timeseries file

        Raises:
            TimeSeriesException: if file was not found, ill-formatted, or value was invalid
        """
        if not self._time_series_is_registered(identifier):
            self._register_time_series(identifier)

    def _time_series_is_registered(self, identifier: Union[str, int, float]) -> bool:
        """Returns True if the value was already registered"""
        return identifier in self._series_by_id

    def _register_time_series(self, identifier: Union[str, int, float]) -> None:
        """Assigns an id to the given `identifier` and loads the time series into a dataframe"""
        self._id_count += 1
        name, series = self._get_name_and_dataframe(identifier)
        self._series_by_id[identifier] = {Entry.ID: self._id_count, Entry.NAME: name, Entry.DATA: series}

    def _get_name_and_dataframe(self, identifier: Union[str, int, float]) -> tuple[str, pd.DataFrame]:
        """Returns name and DataFrame containing the series obtained from the given `identifier`"""
        if isinstance(identifier, str):
            series_path = self._path_resolver.resolve_series_file_path(Path(identifier).as_posix())
            if series_path and os.path.exists(series_path):
                data = pd.read_csv(series_path, sep=";", header=None, comment="#")
                try:
                    return identifier, self._check_and_convert_series(data)
                except TypeError as e:
                    raise log_error(TimeSeriesError(self._ERR_CORRUPT_TIME_SERIES_VALUE.format(identifier), e)) from e
                except ConversionError as e:
                    raise log_error(TimeSeriesError(self._ERR_CORRUPT_TIME_SERIES_KEY.format(identifier), e)) from e
            else:
                message = self._ERR_FILE_NOT_FOUND.format(identifier)
                if self._is_number_string(identifier):
                    message += self._ERR_NUMERIC_STRING
                raise log_error(TimeSeriesError(message))
        else:
            return self._create_timeseries_from_value(identifier)

    def _check_and_convert_series(self, data: pd.DataFrame) -> pd.DataFrame:
        """Ensures validity of time series and convert to required format for writing to disk"""
        additional_columns = data.loc[:, 2:]
        is_empty = additional_columns.dropna(how="all").empty
        if not is_empty:
            log().warning(self._WARN_DATA_IGNORED)
        if data.dtypes[0] != "int64":
            data[0] = [FameTime.convert_string_if_is_datetime(time) for time in data[0]]
        data[1] = [TimeSeriesManager._assert_valid(value) for value in data[1]]
        return data

    @staticmethod
    def _assert_valid(value: Any) -> float:
        """Returns the given `value` if it is a numeric value other than NaN"""
        try:
            value = float(value)
        except ValueError as e:
            raise log_error(TypeError(TimeSeriesManager._ERR_NON_NUMERIC.format(value))) from e
        if math.isnan(value):
            raise log_error(TypeError(TimeSeriesManager._ERR_NAN_VALUE))
        return value

    @staticmethod
    def _is_number_string(identifier: str) -> bool:
        """Returns True if given identifier can be cast to float"""
        try:
            float(identifier)
            return True
        except ValueError:
            return False

    @staticmethod
    def _create_timeseries_from_value(value: Union[int, float]) -> tuple[str, pd.DataFrame]:
        """Returns name and dataframe for a new static timeseries created from the given `value`"""
        if math.isnan(value):
            raise log_error(TimeSeriesError(TimeSeriesManager._ERR_NAN_VALUE))
        data = pd.DataFrame({0: [INT64_MIN, INT64_MAX], 1: [value, value]})
        return TimeSeriesManager._CONSTANT_IDENTIFIER.format(value), data

    def get_series_id_by_identifier(self, identifier: Union[str, int, float]) -> int:
        """
        Returns id for a previously stored time series by given `identifier`

        Args:
            identifier: to get the unique ID for

        Returns:
            unique ID for the given identifier

        Raises:
            TimeSeriesException: if identifier was not yet registered
        """
        if not self._time_series_is_registered(identifier):
            raise log_error(TimeSeriesError(self._ERR_UNREGISTERED_SERIES.format(identifier)))
        return self._series_by_id.get(identifier)[Entry.ID]

    def get_all_series(self) -> list[tuple[int, str, pd.DataFrame]]:
        """Returns iterator over id, name and dataframe of all stored series"""
        if len(self._series_by_id) == 0:
            log().warning(self._WARN_NO_DATA)
        return [(v[Entry.ID], v[Entry.NAME], v[Entry.DATA]) for v in self._series_by_id.values()]

    def reconstruct_time_series(self, timeseries: list[InputData.TimeSeriesDao]) -> None:
        """Reconstructs and stores time series from given list of `timeseries_dao`"""
        for one_series in timeseries:
            self._id_count += 1
            reconstructed = {Entry.ID: one_series.series_id}
            if len(one_series.values) == 1 or (
                len(one_series.values) == 2 and one_series.values[0] == one_series.values[1]
            ):
                reconstructed[Entry.NAME] = one_series.values[0]
                reconstructed[Entry.DATA] = None
            else:
                reconstructed[Entry.NAME] = self._get_cleaned_file_name(one_series.series_name)
                reconstructed[Entry.DATA] = pd.DataFrame(
                    {self._KEY_ROW_TIME: list(one_series.time_steps), self._KEY_ROW_VALUE: list(one_series.values)}
                )
            self._series_by_id[one_series.series_id] = reconstructed

    def _get_cleaned_file_name(self, timeseries_name: str):
        if Path(timeseries_name).suffix.lower() == CSV_FILE_SUFFIX:
            filename = Path(timeseries_name).name
        else:
            filename = clean_up_file_name(timeseries_name) + CSV_FILE_SUFFIX
        return str(Path(self._TIMESERIES_RECONSTRUCTION_PATH, filename))

    def get_reconstructed_series_by_id(self, series_id: int) -> str:
        """Return name or path for given `series_id` if series these are identified by their number.
        Use this only if series were added via `reconstruct_time_series`"""
        if series_id < 0 or series_id > self._id_count:
            raise log_error(TimeSeriesError(self._ERR_UNREGISTERED_SERIES.format(series_id)))
        return self._series_by_id[series_id][Entry.NAME]
