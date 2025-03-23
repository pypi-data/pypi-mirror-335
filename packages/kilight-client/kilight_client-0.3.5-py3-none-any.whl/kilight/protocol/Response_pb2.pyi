from kilight.protocol import SystemState_pb2 as _SystemState_pb2
from kilight.protocol import SystemInfo_pb2 as _SystemInfo_pb2
from kilight.protocol import CommandResult_pb2 as _CommandResult_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("systemState", "systemInfo", "commandResult")
    SYSTEMSTATE_FIELD_NUMBER: _ClassVar[int]
    SYSTEMINFO_FIELD_NUMBER: _ClassVar[int]
    COMMANDRESULT_FIELD_NUMBER: _ClassVar[int]
    systemState: _SystemState_pb2.SystemState
    systemInfo: _SystemInfo_pb2.SystemInfo
    commandResult: _CommandResult_pb2.CommandResult
    def __init__(self, systemState: _Optional[_Union[_SystemState_pb2.SystemState, _Mapping]] = ..., systemInfo: _Optional[_Union[_SystemInfo_pb2.SystemInfo, _Mapping]] = ..., commandResult: _Optional[_Union[_CommandResult_pb2.CommandResult, _Mapping]] = ...) -> None: ...
