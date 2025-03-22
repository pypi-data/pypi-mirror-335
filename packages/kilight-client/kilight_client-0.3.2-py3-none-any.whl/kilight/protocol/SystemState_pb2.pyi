from kilight.protocol import OutputState_pb2 as _OutputState_pb2
from kilight.protocol import SystemTemperatures_pb2 as _SystemTemperatures_pb2
from kilight.protocol import FanState_pb2 as _FanState_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SystemState(_message.Message):
    __slots__ = ("outputA", "outputB", "temperatures", "fan")
    OUTPUTA_FIELD_NUMBER: _ClassVar[int]
    OUTPUTB_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURES_FIELD_NUMBER: _ClassVar[int]
    FAN_FIELD_NUMBER: _ClassVar[int]
    outputA: _OutputState_pb2.OutputState
    outputB: _OutputState_pb2.OutputState
    temperatures: _SystemTemperatures_pb2.SystemTemperatures
    fan: _FanState_pb2.FanState
    def __init__(self, outputA: _Optional[_Union[_OutputState_pb2.OutputState, _Mapping]] = ..., outputB: _Optional[_Union[_OutputState_pb2.OutputState, _Mapping]] = ..., temperatures: _Optional[_Union[_SystemTemperatures_pb2.SystemTemperatures, _Mapping]] = ..., fan: _Optional[_Union[_FanState_pb2.FanState, _Mapping]] = ...) -> None: ...
