from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SystemTemperatures(_message.Message):
    __slots__ = ("driver", "powerSupply")
    DRIVER_FIELD_NUMBER: _ClassVar[int]
    POWERSUPPLY_FIELD_NUMBER: _ClassVar[int]
    driver: int
    powerSupply: int
    def __init__(self, driver: _Optional[int] = ..., powerSupply: _Optional[int] = ...) -> None: ...
