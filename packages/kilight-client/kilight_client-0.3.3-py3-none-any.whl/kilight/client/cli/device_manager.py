import logging

from .config_manager import ConfigManager
from kilight.client import Device

_LOGGER = logging.getLogger(__name__)


class DeviceManager:

    def __init__(self, config: ConfigManager):
        self._config = config
        self._device = Device(config.host, config.port)

    async def __aenter__(self) -> "DeviceManager":
        await self.device.open_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.device.disconnect()

    @property
    def config(self) -> ConfigManager:
        return self._config

    @property
    def device(self) -> Device:
        return self._device