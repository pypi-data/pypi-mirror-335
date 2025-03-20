#!/usr/bin/env python3
"""
# Wiser API Version 2

angelosantagata@gmail.com
msparker@sky.com


https://github.com/asantaga/wiserheatingapi


This API allows you to get information from and control your wiserhub.
"""

import pathlib
from datetime import datetime
from typing import Optional

from aioWiserHeatAPI.helpers.version import Version

from . import __VERSION__, _LOGGER
from .cli import log_response_to_file
from .const import (
    DEFAULT_AWAY_MODE_TEMP,
    DEFAULT_DEGRADED_TEMP,
    MAX_BOOST_INCREASE,
    OPENTHERMV2_MIN_VERSION,
    TEMP_ERROR,
    TEMP_HW_OFF,
    TEMP_HW_ON,
    TEMP_MAXIMUM,
    TEMP_MINIMUM,
    TEMP_OFF,
    WISERHUBDOMAIN,
    WISERHUBNETWORK,
    WISERHUBOPENTHERM,
    WISERHUBOPENTHERMV2,
    WISERHUBSCHEDULES,
    WISERHUBSTATUS,
    WiserUnitsEnum,
)
from .devices import _WiserDeviceCollection
from .exceptions import (
    WiserHubAuthenticationError,
    WiserHubConnectionError,
    WiserHubRESTError,
    WiserScheduleError,
)
from .heating import _WiserHeatingChannelCollection
from .helpers.automations import _WiserHeatingChannelAutomations
from .helpers.status import WiserStatus
from .hot_water import _WiserHotwater
from .moments import _WiserMomentCollection
from .rest_controller import _WiserConnectionInfo, _WiserRestController
from .room import _WiserRoomCollection
from .schedule import WiserScheduleTypeEnum, _WiserScheduleCollection
from .system import _WiserSystem


class WiserAPI:
    """
    Main api class to access all entities and attributes of wiser system
    """

    def __init__(
        self,
        host: str,
        secret: str,
        port: Optional[int] = 80,
        units: Optional[WiserUnitsEnum] = WiserUnitsEnum.metric,
        extra_config_file: Optional[str] = None,
        enable_automations: Optional[bool] = True,
    ):
        # Connection variables
        self._wiser_api_connection = _WiserConnectionInfo()
        self._wiser_rest_controller = None

        # Set connection params
        self._wiser_api_connection.host = host
        self._wiser_api_connection.secret = secret
        self._wiser_api_connection.port = port
        self._wiser_api_connection.units = units
        self._wiser_api_connection.extra_config_file = extra_config_file
        self._wiser_api_connection.enable_automations = enable_automations

        # Hub Data
        self._domain_data = {}
        self._network_data = {}
        self._schedule_data = {}
        self._opentherm_data = {}
        self._status_data = {}

        # Data stores for exposed properties
        self._devices = None
        self._hotwater = None
        self._heating_channels = None
        self._moments = None
        self._rooms = None
        self._schedules = None
        self._system = None

        self._enable_automations = enable_automations
        self._extra_config_file = extra_config_file
        self._extra_config = None

        # Log initialisation info
        _LOGGER.info(
            f"WiserHub API v{__VERSION__} Initialised - Host: {host}, Units: {self._wiser_api_connection.units.name.title()}, Extra Config: {self._extra_config_file}, Automations: {self._enable_automations}"
        )

        if (
            self._wiser_api_connection.host is not None
            and self._wiser_api_connection.secret is not None
        ):
            # Create an instance of the rest controller
            self._wiser_rest_controller = _WiserRestController(
                wiser_connection_info=self._wiser_api_connection
            )
        else:
            raise WiserHubConnectionError(
                "Missing or incomplete connection information"
            )

    async def read_hub_data(self):
        """Update data objects form the hub."""
        await self._build_objects()

        # Run automations
        if self._enable_automations:
            automations = _WiserHeatingChannelAutomations(
                self._wiser_rest_controller, self.heating_channels
            )
            if await automations.run_automations():
                await self._build_objects()

    async def _get_hub_data(self) -> bool:
        try:
            start_time = datetime.now()
            self._domain_data = await self._wiser_rest_controller.get_hub_data(
                WISERHUBDOMAIN
            )
            self._network_data = await self._wiser_rest_controller.get_hub_data(
                WISERHUBNETWORK
            )
            self._schedule_data = await self._wiser_rest_controller.get_hub_data(
                WISERHUBSCHEDULES
            )
            try:
                self._status_data = await self._wiser_rest_controller.get_hub_data(
                    WISERHUBSTATUS
                )
            except WiserHubRESTError:
                self._status_data = {}

            # Only get opentherm data if connected
            opentherm = self._domain_data.get("System", {}).get(
                "OpenThermConnectionStatus", ""
            )
            if opentherm and opentherm == "Connected" or True:
                fw_version = Version(
                    self._domain_data.get("System", {}).get(
                        "ActiveSystemVersion", "1.0.0"
                    )
                )
                hw_version = self._domain_data.get("System", {}).get(
                    "HardwareGeneration", 1
                )
                self._opentherm_data = await self._wiser_rest_controller.get_hub_data(
                    WISERHUBOPENTHERMV2
                    if hw_version == 2 and fw_version >= OPENTHERMV2_MIN_VERSION
                    else WISERHUBOPENTHERM,
                    False,
                )
        except (
            WiserHubConnectionError,
            WiserHubAuthenticationError,
            WiserHubRESTError,
            Exception,
        ) as ex:
            _LOGGER.debug("Update from Wiser hub failed. %s", ex)
            raise ex
        else:
            # Set hub name on rest controller
            self._wiser_rest_controller._hub_name = (
                self._network_data.get("Station", {})
                .get("NetworkInterface", {})
                .get("HostName", "")
            )

            _LOGGER.debug(
                "Update from %s successful and took %ss",
                self._wiser_rest_controller._hub_name,
                (datetime.now() - start_time).total_seconds(),
            )
            return True

    async def _build_objects(self):
        """Read all data from hub and populate objects"""

        # Read data from hub
        try:
            await self._get_hub_data()

            # load extra data
            self._wiser_rest_controller._extra_config_file = self._extra_config_file
            await self._wiser_rest_controller.get_extra_config_data()

            if self._domain_data != {} and self._network_data != {}:
                # System Object
                _device_data = self._domain_data.get("Device", [])
                self._system = _WiserSystem(
                    self._wiser_rest_controller,
                    self._domain_data,
                    self._network_data,
                    _device_data,
                    self._opentherm_data,
                )

                # Schedules Collection
                self._schedules = _WiserScheduleCollection(
                    self._wiser_rest_controller,
                    self._schedule_data,
                    self._system.sunrise_times,
                    self._system.sunset_times,
                )

                # Devices Collection
                self._devices = _WiserDeviceCollection(
                    self._wiser_rest_controller,
                    self._domain_data,
                    self._schedules,
                )

                # Rooms Collection
                room_data = self._domain_data.get("Room", [])
                self._rooms = _WiserRoomCollection(
                    self._wiser_rest_controller,
                    room_data,
                    self._schedules.get_by_type(WiserScheduleTypeEnum.heating),
                    self._devices,
                    self._enable_automations,
                )

                # Hot Water
                if self._domain_data.get("HotWater"):
                    schedule = self._schedules.get_by_id(
                        WiserScheduleTypeEnum.onoff,
                        self._domain_data.get("HotWater")[0].get("ScheduleId", 0),
                    )
                    self._hotwater = _WiserHotwater(
                        self._wiser_rest_controller,
                        self._domain_data.get("HotWater", {})[0],
                        schedule,
                    )

                # Heating Channels
                if self._domain_data.get("HeatingChannel"):
                    self._heating_channels = _WiserHeatingChannelCollection(
                        self._domain_data.get("HeatingChannel"), self._rooms
                    )

                # Moments
                if self._domain_data.get("Moment"):
                    self._moments = _WiserMomentCollection(
                        self._wiser_rest_controller,
                        self._domain_data.get("Moment"),
                    )

                # If gets here with no exceptions then success and return true
                return True
        except (
            WiserHubConnectionError,
            WiserHubAuthenticationError,
            WiserHubRESTError,
            Exception,
        ) as ex:
            raise ex

    # API properties
    @property
    def api_parameters(self):
        """Rest control api parameters."""
        return self._wiser_rest_controller._api_parameters

    @property
    def devices(self) -> _WiserDeviceCollection:
        """List of device entities attached to the Wiser Hub"""
        return self._devices

    @property
    def heating_channels(self) -> _WiserHeatingChannelCollection:
        """List of heating channel entities on the Wiser Hub"""
        return self._heating_channels

    @property
    def hotwater(self) -> _WiserHotwater:
        """List of hot water entities on the Wiser Hub"""
        return self._hotwater

    @property
    def moments(self) -> _WiserMomentCollection:
        """List of moment entities on the Wiser Hub"""
        return self._moments

    @property
    def rooms(self) -> _WiserRoomCollection:
        """List of room entities configured on the Wiser Hub"""
        return self._rooms

    @property
    def schedules(self) -> _WiserScheduleCollection:
        """List of schedules"""
        return self._schedules

    @property
    def status(self) -> WiserStatus:
        """Hub status info"""
        return WiserStatus(self._status_data)

    @property
    def system(self) -> _WiserSystem:
        """Entity of the Wiser Hub"""
        return self._system

    @property
    def units(self) -> WiserUnitsEnum:
        """Get or set units for temperature"""
        return self._wiser_api_connection.units

    @units.setter
    def units(self, units: WiserUnitsEnum):
        self._wiser_api_connection.units = units

    @property
    def version(self):
        """Return api version."""
        return __VERSION__

    @property
    def raw_hub_data(self):
        """Return raw hub data."""
        return {
            "Domain": self._domain_data,
            "Network": self._network_data,
            "Schedule": self._schedule_data,
            "OpenTherm": self._opentherm_data,
            "Status": self._status_data,
        }

    def output_raw_hub_data(
        self, data_class: str, filename: str, file_path: str
    ) -> bool:
        """Output raw hub data to json file"""
        # Get correct endpoint
        if data_class.lower() == "domain":
            endpoint = WISERHUBDOMAIN
        elif data_class.lower() == "network":
            endpoint = WISERHUBNETWORK
        elif data_class == "schedules":
            endpoint = WISERHUBSCHEDULES
        else:
            endpoint = None

        # Get raw json data
        if endpoint:
            data = self._wiser_rest_controller.get_hub_data(endpoint)
            try:
                if data:
                    # Write out to file
                    log_response_to_file(data, filename, False, pathlib.Path(file_path))
                    return True
            except Exception as ex:
                _LOGGER.error(ex)
                return False
