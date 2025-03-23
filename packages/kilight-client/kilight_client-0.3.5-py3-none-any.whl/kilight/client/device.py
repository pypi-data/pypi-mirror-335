import logging
from dataclasses import replace
from typing import Callable

from kilight.protocol import OutputIdentifier
from .const import DEFAULT_PORT
from .models import DeviceState
from .connector import Connector
from .types import WhiteLevels
from .util import color_temp_to_white_levels

_LOGGER = logging.getLogger(__name__)


class Device:
    def __init__(self, host: str, port: int = DEFAULT_PORT, **kwargs):
        self._connector: Connector = Connector(host, port, **kwargs)
        self._state: DeviceState = DeviceState()
        self._callbacks: list[Callable[[DeviceState], None]] = []

    @property
    def connector(self) -> Connector:
        return self._connector

    @property
    def state(self) -> DeviceState:
        return self._state

    @property
    def name(self) -> str:
        if self.state.model is None:
            return f"KiLight at {self.connector.host}:{self.connector.port}"
        return self.state.model

    async def open_connection(self):
        await self.connector.open_connection()

    async def disconnect(self):
        await self.connector.disconnect()

    async def update_state(self):
        if self.state.model is None:
            _LOGGER.debug("Reading state and system info...")
            self._state = await self.connector.read_system_info_and_state(self._state)
            self._fire_callbacks()
            return

        _LOGGER.debug("Reading state...")
        self._state = await self.connector.read_state(self.state)
        _LOGGER.debug("%s State: %s", self.name, self.state)
        self._fire_callbacks()

    async def write_output(self, output: OutputIdentifier, **output_fields_to_update):
        if output == OutputIdentifier.OutputA:
            updated_output = self.state.output_a
        elif output == OutputIdentifier.OutputB and self.state.output_b is not None:
            updated_output = self.state.output_b
        else:
            return

        updated_output = replace(updated_output, **output_fields_to_update)
        _LOGGER.debug("%s Set Output %s = %s...",
                      self.name,
                      OutputIdentifier.Name(output),
                      updated_output)
        self._state = await self.connector.write_update_and_read_state(self._state, output, updated_output)
        _LOGGER.debug("%s State Updated: %s", self.name, self.state)
        self._fire_callbacks()

    async def update_output_from_parts(self, output: OutputIdentifier, **kwargs):
        if output == OutputIdentifier.OutputA:
            updated_output = self.state.output_a
        elif output == OutputIdentifier.OutputB and self.state.output_b is not None:
            updated_output = self.state.output_b
        else:
            return

        if 'rgbcw_color' in kwargs:
            rgbcw_color: tuple[int, int, int, int, int] = kwargs['rgbcw_color']
            _LOGGER.debug("%s Output %s: Set rgbcw_color: %s",
                          self.name,
                          OutputIdentifier.Name(output),
                          rgbcw_color)
            updated_output = replace(updated_output,
                                      red=rgbcw_color[0],
                                      green=rgbcw_color[1],
                                      blue=rgbcw_color[2],
                                      cold_white=rgbcw_color[3],
                                      warm_white=rgbcw_color[4])

        if 'color_temp' in kwargs:
            color_temp: int = kwargs['color_temp']
            _LOGGER.debug("%s Output %s: Set color_temp: %s",
                          self.name,
                          OutputIdentifier.Name(output),
                          color_temp)
            white_levels: WhiteLevels = color_temp_to_white_levels(color_temp)
            updated_output = replace(updated_output,
                                      red=0,
                                      green=0,
                                      blue=0,
                                      cold_white=white_levels.cold_white,
                                      warm_white=white_levels.warm_white)

        if 'brightness' in kwargs:
            brightness: int = kwargs['brightness']
            _LOGGER.debug("%s Output %s: Set brightness: %s",
                          self.name,
                          OutputIdentifier.Name(output),
                          brightness)
            updated_output = replace(updated_output, brightness=brightness)

        if 'power_on' in kwargs:
            power_on: bool = kwargs['power_on']
            _LOGGER.debug("%s Output %s: Set power_on: %s",
                          self.name,
                          OutputIdentifier.Name(output),
                          power_on)
            updated_output = replace(updated_output, power_on=power_on)

        self._state = await self.connector.write_update_and_read_state(self._state, output, updated_output)
        _LOGGER.debug("%s State Updated: %s", self.name, self.state)
        self._fire_callbacks()

    def register_callback(self, callback: Callable[[DeviceState], None]) -> Callable[[], None]:
        """Register a callback to be called when the state changes."""
        def unregister_callback() -> None:
            self._callbacks.remove(callback)

        self._callbacks.append(callback)
        return unregister_callback

    def _fire_callbacks(self) -> None:
        """Fire the callbacks."""
        for callback in self._callbacks:
            callback(self.state)
