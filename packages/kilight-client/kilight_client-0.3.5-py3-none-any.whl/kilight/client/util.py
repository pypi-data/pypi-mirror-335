from __future__ import annotations

import logging

from .const import MIN_COLOR_TEMP, MAX_COLOR_TEMP
from .types import WhiteLevels

_LOGGER = logging.getLogger(__name__)


def color_temp_to_white_levels(temperature: int,
                               min_temp: int = MIN_COLOR_TEMP,
                               max_temp: int = MAX_COLOR_TEMP) -> WhiteLevels:
    temperature = min(max(min_temp, temperature), max_temp)
    warm = ((max_temp - temperature) / (max_temp - min_temp))
    cold = 1.0 - warm
    return WhiteLevels(round(255 * warm), round(255 * cold))


def white_levels_to_color_temp(warm_white: int,
                               cool_white: int,
                               min_temp: int = MIN_COLOR_TEMP,
                               max_temp: int = MAX_COLOR_TEMP) -> int:
    if not (0 <= warm_white <= 255):
        raise ValueError(f"Warm white brightness value {warm_white} is not valid and must be between 0 and 255")
    if not (0 <= cool_white <= 255):
        raise ValueError(f"Cool white brightness value {cool_white} is not valid and must be between 0 and 255")
    warm = warm_white / 255
    cold = cool_white / 255
    total_brightness = warm + cold
    if total_brightness == 0:
        temperature: float = min_temp
    else:
        temperature = ((cold / total_brightness) * (max_temp - min_temp)) + min_temp
    return round(temperature)
