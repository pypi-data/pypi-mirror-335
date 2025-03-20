import hashlib
import inspect
from typing import Union
from uuid import UUID

from .. import _LOGGER
from ..const import (
    TEXT_UNKNOWN,
    WISERDEVICE,
    WiserAwayActionEnum,
    WiserDeviceModeEnum,
    WiserShutterAwayActionEnum,
)
from ..helpers.misc import is_value_in_list
from ..helpers.signal import _WiserSignalStrength
from ..rest_controller import _WiserRestController


class _WiserDevice(object):
    """Class representing a wiser heating device"""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        endpoint: str,
        data: dict,
        device_type_data: dict,
        schedule: dict = None,
    ):
        self._away_action = None
        self._data = data
        self._device_type_data = device_type_data
        self._wiser_rest_controller = wiser_rest_controller
        self._endpoint = endpoint

    async def _send_command(self, cmd: dict, device_level: bool = False):
        """
        Send control command to the smart plug
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        if device_level:
            result = await self._wiser_rest_controller._send_command(
                WISERDEVICE.format(self.id), cmd
            )
            if result:
                self._data = result
        else:
            result = await self._wiser_rest_controller._send_command(
                self._endpoint.format(self.id), cmd
            )
            if result:
                self._device_type_data = result
        if result:
            _LOGGER.debug(
                "Wiser device - {} command successful".format(
                    inspect.stack()[1].function
                )
            )
            return True
        return False

    @property
    def device_lock_enabled(self) -> bool:
        """Get or set device lock"""
        return self._data.get("DeviceLockEnabled", False)

    async def set_device_lock_enabled(self, enabled: bool = False):
        if await self._send_command({"DeviceLockEnabled": enabled}, True):
            self._device_lock_enabled = enabled
            return True

    @property
    def device_type(self) -> str:
        """Get the device types (hub v2 only)"""
        return self._data.get("Type", TEXT_UNKNOWN)

    @property
    def device_type_id(self) -> int:
        """Get the device id for the specific device type"""
        return self._device_type_data.get("id")

    @property
    def identify(self) -> bool:
        """Get or set if the identify function is enabled"""
        return self._data.get("IdentifyActive", False)

    async def set_identify(self, enabled: bool = False):
        if await self._send_command({"Identify": enabled}, True):
            self._indentify_active = enabled
            return True

    @property
    def firmware_version(self) -> str:
        """Get firmware version of device"""
        return self._data.get("ActiveFirmwareVersion", TEXT_UNKNOWN)

    @property
    def id(self) -> int:
        """Get id of device"""
        return self._data.get("id")

    @property
    def model(self) -> str:
        """Get model of device"""
        # Lights, shutters and power tags currently have model identifier as Unknowm
        # return (
        #    self._data.get("ProductType", TEXT_UNKNOWN)
        #    if self._data.get("ModelIdentifier") == TEXT_UNKNOWN
        #    else self._data.get("ModelIdentifier", TEXT_UNKNOWN)
        # )

        if self.product_model not in ["", TEXT_UNKNOWN]:
            return self._data.get("ProductModel")
        elif self._data.get("ModelIdentifier") != TEXT_UNKNOWN:
            return self._data.get("ModelIdentifier")
        else:
            return self.product_identifier

    @property
    def name(self) -> str:
        """Get name of device."""
        if self._data.get("Name"):
            return self._data.get("Name")
        return f"{self.product_type}-{self.id}"

    @property
    def node_id(self) -> int:
        """Get zigbee node id of device"""
        return self._data.get("NodeId", 0)

    @property
    def ota_hardware_version(self) -> int:
        """Get ota hardware version"""
        return self._data.get("OtaHardwareVersion", 0)

    @property
    def ota_version(self) -> int:
        """Get ota software version"""
        return self._data.get("OtaVersion", 0)

    @property
    def product_identifier(self) -> str:
        """Get product identifier of device"""
        return self._data.get("ProductIdentifier", TEXT_UNKNOWN)

    @property
    def product_model(self) -> str:
        """Get product model of device"""
        return self._data.get("ProductModel", TEXT_UNKNOWN)

    @property
    def parent_node_id(self) -> int:
        """Get zigbee node id of device this device is connected to"""
        return self._data.get("ParentNodeId", 0)

    @property
    def product_type(self) -> str:
        """Get product type of device"""
        return self._data.get("ProductType", TEXT_UNKNOWN)

    @property
    def room_id(self) -> int:
        """Get room id of the device."""
        return self._device_type_data.get("RoomId", self._data.get("RoomId", 0))

    @property
    def serial_number(self) -> str:
        """Get serial number of device"""
        return self._data.get("SerialNumber", TEXT_UNKNOWN)

    @property
    def signal(self) -> _WiserSignalStrength:
        """Get zwave network information"""
        return _WiserSignalStrength(self._data)

    # Added by LGO
    @property
    def endpoint(self) -> int:
        """Get endpoint"""
        return self._device_type_data.get("Endpoint", 0)

    # Device type Zigbee
    @property
    def type_comm(self) -> str:
        """Get type of zigbee device"""
        return self._data.get("Type", TEXT_UNKNOWN)

    # UUID Zigbee
    @property
    def uuid(self) -> str:
        """Get UUID zigbee"""
        if uuid := self._device_type_data.get("UUID"):
            return uuid
        uname = (
            f"{self.product_type}_{self.serial_number}_{self.id}_{self.device_type_id}"
        )
        hexstr = hashlib.md5(uname.encode("UTF-8")).hexdigest()
        return UUID(hex=hexstr)

    # END Added by LGO


class _WiserElectricalDevice(_WiserDevice):
    """Class representing a wiser electrical device"""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        endpoint: str,
        data: dict,
        device_type_data: dict,
        schedule: dict,
    ):
        super().__init__(
            wiser_rest_controller, endpoint, data, device_type_data, schedule
        )
        self._schedule = schedule

        # Add device id to schedule
        if self._schedule:
            self._schedule._assignments.append(
                {"id": self.device_type_id, "name": self.name}
            )
            self._schedule._device_ids.append(self.id)

    @property
    def available_modes(self):
        """Get available modes"""
        return [mode.value for mode in WiserDeviceModeEnum]

    @property
    def available_away_mode_actions(self):
        """Get available away mode actions"""
        return [action.value for action in WiserAwayActionEnum]

    @property
    def away_mode_action(self) -> str:
        """Get or set the away action of the device (off or no change)"""
        return self._device_type_data.get("AwayAction", TEXT_UNKNOWN)

    async def set_away_mode_action(
        self,
        action: Union[WiserAwayActionEnum, WiserShutterAwayActionEnum, str],
    ) -> bool:
        if isinstance(action, WiserAwayActionEnum) or isinstance(
            action, WiserShutterAwayActionEnum
        ):
            action = action.value

        if is_value_in_list(action, self.available_away_mode_actions):
            if await self._send_command({"AwayAction": action}):
                self._away_action = action
                return True
        else:
            raise ValueError(
                f"{action} is not a valid away mode action.  "
                f"Valid modes are {self.available_away_mode_actions}"
            )

    @property
    def device_type_id(self) -> int:
        """Get the device id for the specific device type"""
        return self._device_type_data.get("id")

    @property
    def mode(self) -> str:
        """Get or set the current mode of the device (Manual or Auto)"""
        return self._device_type_data.get("Mode", TEXT_UNKNOWN)

    async def set_mode(self, mode: Union[WiserDeviceModeEnum, str]) -> bool:
        if isinstance(mode, WiserDeviceModeEnum):
            mode = mode.value
        if is_value_in_list(mode, self.available_modes):
            return await self._send_command({"Mode": mode.title()})
        else:
            raise ValueError(
                f"{mode} is not a valid mode.  Valid modes are {self.available_modes}"
            )

    @property
    def name(self) -> str:
        if self._data.get("Name"):
            return self._data.get("Name")
        return self._device_type_data.get("Name", TEXT_UNKNOWN)

    async def set_name(self, name: str) -> bool:
        if await self._send_command({"Name": name}):
            return True

    @property
    def schedule(self):
        """Get the schedule of the device"""
        return self._schedule

    @property
    def schedule_id(self) -> int:
        """Get the schedule id for the device"""
        return self._device_type_data.get("ScheduleId", 0)
