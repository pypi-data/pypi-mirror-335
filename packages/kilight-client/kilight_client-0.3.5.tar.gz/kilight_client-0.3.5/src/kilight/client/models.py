from __future__ import annotations

from dataclasses import dataclass

from kilight.protocol import (OutputIdentifier,
                              OutputState as ProtocolOutputState,
                              WriteOutput as ProtocolWriteOutput, \
                              VersionInfo as ProtocolVersionInfo,
                              Color as ProtocolColor)
from .util import white_levels_to_color_temp


@dataclass(frozen=True)
class TemperatureState:
    celsius: float | None = None


@dataclass(frozen=True)
class OutputState:
    power_on: bool = False
    red: int = 0
    green: int = 0
    blue: int = 0
    cold_white: int = 0
    warm_white: int = 0
    brightness: int = 0
    current: float = 0.0
    temperature: TemperatureState | None = None

    @staticmethod
    def from_protocol(protocol_output_state: ProtocolOutputState) -> OutputState:
        temperature_state = None
        if protocol_output_state.HasField("temperature"):
            temperature_state = TemperatureState(celsius=protocol_output_state.temperature / 100)

        return OutputState(
            red=protocol_output_state.color.red,
            green=protocol_output_state.color.green,
            blue=protocol_output_state.color.blue,
            cold_white=protocol_output_state.color.coldWhite,
            warm_white=protocol_output_state.color.warmWhite,
            brightness=protocol_output_state.brightness,
            power_on=protocol_output_state.on,
            current=protocol_output_state.current / 1000,
            temperature=temperature_state
        )

    def to_protocol(self, output_id: OutputIdentifier = OutputIdentifier.Invalid) -> ProtocolWriteOutput:
        return ProtocolWriteOutput(
            outputId=output_id,
            color=ProtocolColor(
                red=self.red,
                green=self.green,
                blue=self.blue,
                coldWhite=self.cold_white,
                warmWhite=self.warm_white,
            ),
            brightness=self.brightness,
            on=self.power_on
        )

    @property
    def rgbcw(self) -> tuple[int, int, int, int, int]:
        return self.red, self.green, self.blue, self.cold_white, self.warm_white

    @property
    def color_temp(self) -> int:
        return white_levels_to_color_temp(self.warm_white, self.cold_white)


@dataclass(frozen=True)
class VersionInfo:
    major: int = 0
    minor: int = 0
    patch: int = 0

    @staticmethod
    def from_protocol(protocol_version_info: ProtocolVersionInfo) -> VersionInfo:
        return VersionInfo(
            major=protocol_version_info.major,
            minor=protocol_version_info.minor,
            patch=protocol_version_info.patch
        )

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class DeviceState:
    hardware_id: str | None = None
    manufacturer_name: str | None = None
    model: str | None = None
    hardware_version: VersionInfo | None = None
    firmware_version: VersionInfo | None = None

    output_a: OutputState = OutputState()
    output_b: OutputState | None = None

    driver_temperature: TemperatureState = TemperatureState()
    power_supply_temperature: TemperatureState | None = None

    fan_speed: int | None = None
    fan_drive_percentage: float | None = None


@dataclass(frozen=True)
class DiscoveredDeviceInfo:
    name: str
    hostname: str
    port: int | None
    hardware_id: str | None
