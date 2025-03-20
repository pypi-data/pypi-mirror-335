import inspect

from . import _LOGGER
from .const import TEXT_UNKNOWN, WISERSYSTEM
from .rest_controller import _WiserRestController


class _WiserMoment(object):
    def __init__(
        self, wiser_rest_controller: _WiserRestController, moment_data: dict
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._moment_data = moment_data

    async def _send_command(self, cmd: dict) -> bool:
        """
        Send system control command to Wiser Hub
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        result = await self._wiser_rest_controller._send_command(
            WISERSYSTEM, cmd
        )
        if result:
            _LOGGER.debug(
                "Wiser hub - {} command successful".format(
                    inspect.stack()[1].function
                )
            )
            return True
        return False

    @property
    def id(self) -> int:
        return self._moment_data.get("id", 0)

    @property
    def name(self) -> str:
        return self._moment_data.get("Name", TEXT_UNKNOWN)

    async def activate(self):
        """Activate moment"""
        return await self._send_command({"TriggerMoment": self.id})


class _WiserMomentCollection(object):
    def __init__(
        self, wiser_rest_controller: _WiserRestController, moments_data: dict
    ):
        self._moments_data = moments_data
        self._moments = []
        self._wiser_rest_controller = wiser_rest_controller
        self._build()

    def _build(self):
        for moment in self._moments_data:
            self._moments.append(
                _WiserMoment(self._wiser_rest_controller, moment)
            )

    @property
    def all(self) -> list[_WiserMoment]:
        """Return list of moments"""
        return self._moments

    @property
    def count(self) -> int:
        """Count of moments"""
        return len(self._moments)

    def get_by_id(self, moment_id: int) -> _WiserMoment:
        try:
            return [moment for moment in self.all if moment.id == moment_id][0]
        except IndexError:
            return None
