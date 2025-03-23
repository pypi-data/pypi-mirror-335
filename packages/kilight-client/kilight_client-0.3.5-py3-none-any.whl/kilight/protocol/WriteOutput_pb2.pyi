from kilight.protocol import Color_pb2 as _Color_pb2
from kilight.protocol import OutputIdentifier_pb2 as _OutputIdentifier_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WriteOutput(_message.Message):
    __slots__ = ("outputId", "color", "brightness", "on")
    OUTPUTID_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    ON_FIELD_NUMBER: _ClassVar[int]
    outputId: _OutputIdentifier_pb2.OutputIdentifier
    color: _Color_pb2.Color
    brightness: int
    on: bool
    def __init__(self, outputId: _Optional[_Union[_OutputIdentifier_pb2.OutputIdentifier, str]] = ..., color: _Optional[_Union[_Color_pb2.Color, _Mapping]] = ..., brightness: _Optional[int] = ..., on: bool = ...) -> None: ...
