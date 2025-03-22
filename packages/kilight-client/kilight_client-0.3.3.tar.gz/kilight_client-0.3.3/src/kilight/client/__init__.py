"""kilight.client package for interfacing with KiLight open hardware light controllers."""

__version__ = "0.3.3"

__all__ = [
    "DEFAULT_PORT",
    "MIN_COLOR_TEMP",
    "MAX_COLOR_TEMP",
    "Connector",
    "Device",
    "OutputIdentifier",
    "OutputState",
    "DeviceState"
]

from kilight.protocol import OutputIdentifier

from .const import DEFAULT_PORT, MIN_COLOR_TEMP, MAX_COLOR_TEMP
from .connector import Connector
from .device import Device
from .models import OutputState, DeviceState