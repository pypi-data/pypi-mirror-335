from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Color(_message.Message):
    __slots__ = ("red", "green", "blue", "coldWhite", "warmWhite")
    RED_FIELD_NUMBER: _ClassVar[int]
    GREEN_FIELD_NUMBER: _ClassVar[int]
    BLUE_FIELD_NUMBER: _ClassVar[int]
    COLDWHITE_FIELD_NUMBER: _ClassVar[int]
    WARMWHITE_FIELD_NUMBER: _ClassVar[int]
    red: int
    green: int
    blue: int
    coldWhite: int
    warmWhite: int
    def __init__(self, red: _Optional[int] = ..., green: _Optional[int] = ..., blue: _Optional[int] = ..., coldWhite: _Optional[int] = ..., warmWhite: _Optional[int] = ...) -> None: ...
