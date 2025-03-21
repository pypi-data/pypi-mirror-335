from typing import overload
from enum import Enum
import abc
import datetime
import typing

import QuantConnect
import QuantConnect.Data
import QuantConnect.DownloaderDataProvider.Launcher.Models
import System
import System.Collections.Generic

QuantConnect_DownloaderDataProvider_Launcher_Models_BaseDataDownloadConfig_ParseEnum_TEnum = typing.TypeVar("QuantConnect_DownloaderDataProvider_Launcher_Models_BaseDataDownloadConfig_ParseEnum_TEnum")


class BaseDataDownloadConfig(System.Object, metaclass=abc.ABCMeta):
    """Abstract base class for configuring data download parameters, including common properties and initialization logic."""

    @property
    def start_date(self) -> datetime.datetime:
        """Gets the start date for the data download."""
        ...

    @property.setter
    def start_date(self, value: datetime.datetime) -> None:
        ...

    @property
    def end_date(self) -> datetime.datetime:
        """Gets the end date for the data download."""
        ...

    @property.setter
    def end_date(self, value: datetime.datetime) -> None:
        ...

    @property
    def resolution(self) -> QuantConnect.Resolution:
        """Gets or sets the resolution of the downloaded data."""
        ...

    @property
    def market_name(self) -> str:
        """Gets or sets the market name for which the data will be downloaded."""
        ...

    @property
    def security_type(self) -> QuantConnect.SecurityType:
        """Gets the type of security for which the data is being downloaded."""
        ...

    @property.setter
    def security_type(self, value: QuantConnect.SecurityType) -> None:
        ...

    @property
    def tick_type(self) -> QuantConnect.TickType:
        """Gets or sets the type of tick data to be downloaded."""
        ...

    @property
    @abc.abstractmethod
    def data_type(self) -> typing.Type:
        """The type of data based on TickTypes"""
        ...

    @property
    def symbols(self) -> System.Collections.Generic.IReadOnlyCollection[QuantConnect.Symbol]:
        """Gets the list of symbols for which the data will be downloaded."""
        ...

    @overload
    def __init__(self) -> None:
        """
        Initializes a new instance of the BaseDataDownloadConfig class.
        
        This method is protected.
        """
        ...

    @overload
    def __init__(self, tickType: QuantConnect.TickType, securityType: QuantConnect.SecurityType, resolution: QuantConnect.Resolution, startDate: typing.Union[datetime.datetime, datetime.date], endDate: typing.Union[datetime.datetime, datetime.date], marketName: str, symbols: System.Collections.Generic.List[QuantConnect.Symbol]) -> None:
        """
        Initializes a new instance of the DataDownloadConfig class with the specified parameters.
        
        This method is protected.
        
        :param tickType: The type of tick data to be downloaded.
        :param securityType: The type of security for which data is being downloaded.
        :param resolution: The resolution of the data being downloaded.
        :param startDate: The start date for the data download range.
        :param endDate: The end date for the data download range.
        :param marketName: The name of the market from which the data is being downloaded.
        :param symbols: A list of symbols for which data is being downloaded.
        """
        ...

    @staticmethod
    def parse_date(date: str) -> datetime.datetime:
        """
        Parses a string to a DateTime using a specific date format.
        
        This method is protected.
        
        :param date: The date string to parse.
        :returns: The parsed DateTime value.
        """
        ...

    @staticmethod
    def parse_enum(value: str) -> QuantConnect_DownloaderDataProvider_Launcher_Models_BaseDataDownloadConfig_ParseEnum_TEnum:
        """
        Parses a string value into an enum of the specified type.
        
        This method is protected.
        
        :param value: The string value to parse.
        :returns: The parsed enum value.
        """
        ...


class DataDownloadConfig(QuantConnect.DownloaderDataProvider.Launcher.Models.BaseDataDownloadConfig):
    """Represents the configuration for downloading data."""

    @property
    def data_type(self) -> typing.Type:
        """Gets the type of data download."""
        ...

    @overload
    def __init__(self) -> None:
        """Initializes a new instance of the DataDownloadConfig class."""
        ...

    @overload
    def __init__(self, tickType: QuantConnect.TickType, securityType: QuantConnect.SecurityType, resolution: QuantConnect.Resolution, startDate: typing.Union[datetime.datetime, datetime.date], endDate: typing.Union[datetime.datetime, datetime.date], marketName: str, symbols: System.Collections.Generic.List[QuantConnect.Symbol]) -> None:
        """
        Initializes a new instance of the DataDownloadConfig class with the specified parameters.
        
        :param tickType: The type of tick data to be downloaded.
        :param securityType: The type of security for which data is being downloaded.
        :param resolution: The resolution of the data being downloaded.
        :param startDate: The start date for the data download range.
        :param endDate: The end date for the data download range.
        :param marketName: The name of the market from which the data is being downloaded.
        :param symbols: A list of symbols for which data is being downloaded.
        """
        ...


class BrokerageDataDownloader(System.Object, QuantConnect.IDataDownloader):
    """Class for downloading data from a brokerage."""

    def __init__(self) -> None:
        """Initializes a new instance of the BrokerageDataDownloader class."""
        ...

    def get(self, data_downloader_get_parameters: QuantConnect.DataDownloaderGetParameters) -> System.Collections.Generic.IEnumerable[QuantConnect.Data.BaseData]:
        """
        Get historical data enumerable for a single symbol, type and resolution given this start and end time (in UTC).
        
        :param data_downloader_get_parameters: model class for passing in parameters for historical data
        :returns: Enumerable of base data for this symbol.
        """
        ...


class DataUniverseDownloadConfig(QuantConnect.DownloaderDataProvider.Launcher.Models.BaseDataDownloadConfig):
    """Represents the configuration for downloading data for a universe of securities."""

    @property
    def data_type(self) -> typing.Type:
        """Gets the type of data universe download."""
        ...

    def __init__(self) -> None:
        """Initializes a new instance of the DataUniverseDownloadConfig class using configuration settings."""
        ...


