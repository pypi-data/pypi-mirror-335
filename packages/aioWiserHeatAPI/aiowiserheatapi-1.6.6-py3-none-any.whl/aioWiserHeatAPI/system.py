import inspect
from datetime import datetime

from . import _LOGGER
from .const import TEXT_ON, TEXT_UNKNOWN, WISERSYSTEM
from .helpers.capabilities import (
    _WiserHubCapabilitiesInfo,
    _WiserHubFeatureCapabilitiesInfo,
)
from .helpers.cloud import _WiserCloud
from .helpers.firmware import _WiserFirmareUpgradeInfo
from .helpers.gps import _WiserGPS
from .helpers.network import _WiserNetwork
from .helpers.opentherm import _WiserOpentherm
from .helpers.signal import _WiserSignalStrength
from .helpers.special_times import sunrise_times, sunset_times
from .helpers.temp import _WiserTemperatureFunctions as tf
from .helpers.zigbee import _WiserZigbee
from .rest_controller import _WiserRestController


class _WiserSystem(object):
    """Class representing a Wiser Hub device"""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        domain_data: dict,
        network_data: dict,
        device_data: dict,
        opentherm_data: dict,
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._data = domain_data
        self._system_data = self._data.get("System", {})

        # Sub classes for system setting values
        self._capability_data = _WiserHubCapabilitiesInfo(
            self._data.get("DeviceCapabilityMatrix", {})
        )
        self._feature_capability_data = _WiserHubFeatureCapabilitiesInfo(
            self._data.get("FeatureCapability", {})
        )
        self._cloud_data = _WiserCloud(
            self._system_data.get("CloudConnectionStatus"),
            self._data.get("Cloud", {}),
        )
        self._device_data = self._get_system_device(device_data)
        self._network_data = _WiserNetwork(
            network_data.get("Station", {}), self._wiser_rest_controller
        )
        self._opentherm_data = _WiserOpentherm(
            self._wiser_rest_controller,
            opentherm_data,
            self._system_data.get("OpenThermConnectionStatus", TEXT_UNKNOWN),
        )
        self._signal = _WiserSignalStrength(self._device_data)
        self._upgrade_data = _WiserFirmareUpgradeInfo(self._data.get("UpgradeInfo", {}))
        self._zigbee_data = _WiserZigbee(self._data.get("Zigbee", {}))

        # Variables to hold values for settabel values
        self._automatic_daylight_saving = self._system_data.get(
            "AutomaticDaylightSaving"
        )
        self._away_mode_affects_hotwater = self._system_data.get(
            "AwayModeAffectsHotWater"
        )
        self._away_mode_target_temperature = self._system_data.get(
            "AwayModeSetPointLimit"
        )
        self._comfort_mode_enabled = self._system_data.get("ComfortModeEnabled")
        self._degraded_mode_target_temperature = self._system_data.get(
            "DegradedModeSetpointThreshold"
        )
        self._eco_mode_enabled = self._system_data.get("EcoModeEnabled")
        self._hub_time = datetime.fromtimestamp(self._system_data.get("UnixTime"))
        self._override_type = self._system_data.get("OverrideType", "")
        self._timezone_offset = self._system_data.get("TimeZoneOffset")
        self._valve_protection_enabled = self._system_data.get("ValveProtectionEnabled")

        # Added by LGO
        # Summer comfort
        self._summer_comfort_enabled = self._system_data.get("SummerComfortEnabled")
        self._indoor_discomfort_temperature = self._system_data.get(
            "IndoorDiscomfortTemperature"
        )
        self._outdoor_discomfort_temperature = self._system_data.get(
            "OutdoorDiscomfortTemperature"
        )
        self._summer_comfort_available = self._system_data.get("SummerComfortAvailable")
        self._summer_discomfort_prevention = self._system_data.get(
            "SummerDiscomfortPrevention"
        )

        # End Added by LGO

    def _get_system_device(self, device_data: dict):
        for device in device_data:
            # Add controller to sytem class
            if device.get("ProductType") == "Controller":
                return device

    async def _send_command(self, cmd: dict, path: str = None) -> bool:
        """
        Send system control command to Wiser Hub
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        if path:
            result = await self._wiser_rest_controller._send_command(
                f"{WISERSYSTEM}/{path}", cmd
            )
        else:
            result = await self._wiser_rest_controller._send_command(WISERSYSTEM, cmd)
        if result:
            _LOGGER.debug(
                "Wiser hub - {} command successful".format(inspect.stack()[1].function)
            )
            return True
        return False

    @property
    def active_system_version(self) -> str:
        """Get current hub firmware version"""
        return self._system_data.get("ActiveSystemVersion", TEXT_UNKNOWN)

    @property
    def automatic_daylight_saving_enabled(self) -> bool:
        """Get or set if auto daylight saving is enabled"""
        return self._automatic_daylight_saving

    async def set_automatic_daylight_saving_enabled(self, enabled: bool):
        if await self._send_command({"AutomaticDaylightSaving": str(enabled).lower()}):
            self._automatic_daylight_saving = enabled
            return True

    @property
    def away_mode_enabled(self) -> bool:
        """Get or set if away mode is enabled"""
        return True if self._override_type == "Away" else False

    async def set_away_mode_enabled(self, enabled: bool):
        if await self._send_command({"RequestOverride": {"Type": 2 if enabled else 0}}):
            self._override_type = "Away" if enabled else ""
            return True

    @property
    def away_mode_affects_hotwater(self) -> bool:
        """Get or set if setting away mode affects hot water"""
        return self._away_mode_affects_hotwater

    async def set_away_mode_affects_hotwater(self, enabled: bool = False):
        if await self._send_command({"AwayModeAffectsHotWater": str(enabled).lower()}):
            self._away_mode_affects_hotwater = enabled
            return True

    @property
    def away_mode_target_temperature(self) -> float:
        """Get or set target temperature for away mode"""
        return tf._from_wiser_temp(self._away_mode_target_temperature)

    async def set_away_mode_target_temperature(self, temp: float):
        temp = tf._to_wiser_temp(temp)
        if await self._send_command({"AwayModeSetPointLimit": temp}):
            self._away_mode_target_temperature = tf._to_wiser_temp(temp)
            return True

    @property
    def boiler_fuel_type(self) -> str:
        """Get boiler fuel type setting"""
        # TODO: Add ability to set to 1 of 3 types
        return self._system_data.get("BoilerSettings", {"FuelType": TEXT_UNKNOWN}).get(
            "FuelType"
        )

    @property
    def brand_name(self) -> str:
        """Get brand name of Wiser hub"""
        return self._system_data.get("BrandName")

    @property
    def capabilities(self) -> _WiserHubCapabilitiesInfo:
        """Get capability info"""
        return self._capability_data

    @property
    def cloud(self) -> _WiserCloud:
        """Get cloud settings"""
        return self._cloud_data

    @property
    def comfort_mode_enabled(self) -> bool:
        """Get or set if comfort mode is enabled"""
        return self._comfort_mode_enabled

    async def set_comfort_mode_enabled(self, enabled: bool):
        if await self._send_command({"ComfortModeEnabled": enabled}):
            self._comfort_mode_enabled = enabled
            return True

    @property
    def degraded_mode_target_temperature(self) -> float:
        """Get or set degraded mode target temperature"""
        return tf._from_wiser_temp(self._degraded_mode_target_temperature)

    async def set_degraded_mode_target_temperature(self, temp: float):
        temp = temp._to_wiser_temp(temp)
        if await self._send_command({"DegradedModeSetpointThreshold": temp}):
            self._degraded_mode_target_temperature = temp
            return True

    @property
    def eco_mode_enabled(self) -> bool:
        """Get or set whether eco mode is enabled"""
        return self._eco_mode_enabled

    async def set_eco_mode_enabled(self, enabled: bool):
        if await self._send_command({"EcoModeEnabled": enabled}):
            self._eco_mode_enabled = enabled
            return True

    @property
    def feature_capabilities(self) -> _WiserHubFeatureCapabilitiesInfo:
        """Get feature capability info"""
        return self._feature_capability_data

    @property
    def firmware_over_the_air_enabled(self) -> bool:
        """Whether firmware updates over the air are enabled on the hub"""
        return self._system_data.get("FotaEnabled")

    @property
    def firmware_version(self) -> str:
        """Get firmware version of device"""
        return self._device_data.get("ActiveFirmwareVersion", TEXT_UNKNOWN)

    @property
    def geo_position(self) -> _WiserGPS:
        """Get geo location information"""
        return _WiserGPS(self._system_data.get("GeoPosition", {}))

    @property
    def hardware_generation(self) -> int:
        """Get hardware generation version"""
        return self._system_data.get("HardwareGeneration", 1)

    @property
    def heating_button_override_state(self) -> bool:
        """Get if heating override button is on"""
        return (
            True
            if self._system_data.get("HeatingButtonOverrideState") == TEXT_ON
            else False
        )

    @property
    def hotwater_button_override_state(self) -> bool:
        """Get if hot water override button is on"""
        return (
            True
            if self._system_data.get("HotWaterButtonOverrideState") == TEXT_ON
            else False
        )

    @property
    def hub_time(self) -> datetime:
        """Get the current time on hub"""
        return self._hub_time

    @property
    def id(self) -> int:
        """Get id of device"""
        return self._device_data.get("id")

    @property
    def is_away_mode_enabled(self) -> bool:
        """Get if away mode is enabled"""
        return True if self._override_type == "Away" else False

    @property
    def model(self) -> str:
        """Get model of device"""
        return self._device_data.get("ModelIdentifier", TEXT_UNKNOWN)

    @property
    def name(self) -> str:
        """Get name of hub"""
        return self.network.hostname

    @property
    def network(self) -> _WiserNetwork:
        """Get network information from hub"""
        return self._network_data

    @property
    def node_id(self) -> int:
        """Get zigbee node id of device"""
        return self._device_data.get("NodeId", 0)

    @property
    def opentherm(self) -> _WiserOpentherm:
        """Get opentherm info"""
        return self._opentherm_data

    @property
    def pairing_status(self) -> str:
        """Get account pairing status"""
        return self._system_data.get("PairingStatus", TEXT_UNKNOWN)

    @property
    def parent_node_id(self) -> int:
        """Get zigbee node id of device this device is connected to"""
        return self._device_data.get("ParentNodeId", 0)

    @property
    def product_type(self) -> str:
        """Get product type of device"""
        return self._device_data.get("ProductType", TEXT_UNKNOWN)

    @property
    def signal(self) -> _WiserSignalStrength:
        """Get zwave network information"""
        return self._signal

    # Added LGO
    @property
    def summer_comfort_enabled(self) -> bool:
        """Get whether summer comfort mode is enabled"""
        return self._summer_comfort_enabled

    async def set_summer_comfort_enabled(self, enabled: bool):
        """Set whether summer comfort mode is enabled"""
        if await self._send_command({"SummerComfortEnabled": enabled}):
            self._summer_comfort_enabled = enabled
            return True

    @property
    def indoor_discomfort_temperature(self) -> float:
        """Get indoor discomfort temperature for summer comfort"""
        return tf._from_wiser_temp(self._indoor_discomfort_temperature)

    async def set_indoor_discomfort_temperature(self, temp: float):
        """Set indoor discomfort temperature for summer comfort"""
        temp = tf._to_wiser_temp(temp)
        if await self._send_command({"IndoorDiscomfortTemperature": temp}):
            self._away_mode_target_temperature = tf._to_wiser_temp(temp)
            return True

    @property
    def outdoor_discomfort_temperature(self) -> float:
        """Get outdoor discomfort temperature for summer comfort"""
        return tf._from_wiser_temp(self._outdoor_discomfort_temperature)

    async def set_outdoor_discomfort_temperature(self, temp: float):
        """Set outdoor discomfort temperature for summer comfort"""
        temp = tf._to_wiser_temp(temp)
        if await self._send_command({"OutdoorDiscomfortTemperature": temp}):
            self._away_mode_target_temperature = tf._to_wiser_temp(temp)
            return True

    @property
    def summer_comfort_available(self) -> bool:
        """Get whether summer comfort mode is available"""
        return self._summer_comfort_available

    @property
    def summer_discomfort_prevention(self) -> bool:
        """Get summer discomfort prevention"""
        return self._summer_discomfort_prevention

    async def set_summer_discomfort_prevention(self, enabled: bool):
        """Set summer discomfort prevention"""
        if await self._send_command({"SummerDiscomfortPrevention": enabled}):
            self._summer_discomfort_prevention = enabled
            return True

    @property
    def type_comm(self) -> str:
        """Get type of zigbee device"""
        return self._device_data.get("Type", TEXT_UNKNOWN)

    @property
    def uuid(self) -> str:
        """Get UUID zigbee"""
        return self._device_data.get("UUID", TEXT_UNKNOWN)

    # PCM features
    @property
    def pcm_version(self) -> str:
        """Get PCM version"""
        return self._system_data.get("PCMVersion", TEXT_UNKNOWN)

    @property
    def pcm_status(self) -> str:
        """Get PCM Status"""
        return self._system_data.get("PCMStatus", TEXT_UNKNOWN)

    @property
    def pcm_device_limit_reached(self) -> bool:
        """Get PCM device limit reached"""
        return self._system_data.get("PCMDeviceLimitReached", False)

    @property
    def can_activate_pcm(self) -> bool:
        """Get Can activate PCM"""
        return self._system_data.get("CanActivatePCM", False)

    # End Added LGO

    @property
    def sunrise_times(self) -> dict[str, str]:
        """Get sunrise times"""
        return sunrise_times(self._system_data.get("SunriseTimes", []))

    @property
    def sunset_times(self) -> dict[str, str]:
        """Get sunset times"""
        return sunset_times(self._system_data.get("SunsetTimes", []))

    @property
    def system_mode(self) -> str:
        """Get current system mode"""
        return self._system_data.get("SystemMode", TEXT_UNKNOWN)

    @property
    def timezone_offset(self) -> int:
        """Get timezone offset in minutes"""
        return self._timezone_offset

    async def set_timezone_offset(self, offset: int):
        if await self._send_command({"TimeZoneOffset": offset}):
            self._timezone_offset = offset
            return True

    @property
    def user_overrides_active(self) -> bool:
        """Get if any overrides are active"""
        return self._system_data.get("UserOverridesActive", False)

    @property
    def valve_protection_enabled(self) -> bool:
        """Get or set if valve protection is enabled"""
        return self._valve_protection_enabled

    async def set_valve_protection_enabled(self, enabled: bool):
        """
        Set the valve protection setting on the wiser hub
        param enabled: turn on or off
        """
        return await self._send_command({"ValveProtectionEnabled": enabled})

    @property
    def zigbee(self) -> _WiserZigbee:
        """Get zigbee info"""
        return self._zigbee_data

    async def allow_add_device(self, allow_time: int = 120):
        """
        Put hub in permit join mode for adding new devices
        """
        return await self._send_command(allow_time, "RequestPermitJoin")

    async def boost_all_rooms(self, inc_temp: float, duration: int) -> bool:
        """
        Boost the temperature of all rooms
        param inc_temp: increase target temperature over current temperature by 0C to 5C
        param duration: the duration to boost the room temperatures in minutes
        return: boolean
        """
        return await self._send_command(
            {
                "RequestOverride": {
                    "Type": "Boost",
                    "DurationMinutes": duration,
                    "IncreaseSetPointBy": tf._to_wiser_temp(inc_temp, "boostDelta"),
                }
            }
        )

    async def cancel_all_overrides(self):
        """
        Cancel all overrides and set room schedule to the current temperature setting for the mode
        return: boolean
        """
        return await self._send_command(
            {"RequestOverride": {"Type": "CancelUserOverrides"}}
        )
