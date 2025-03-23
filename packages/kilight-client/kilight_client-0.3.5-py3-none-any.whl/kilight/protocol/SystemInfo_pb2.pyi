import embedded_proto_options_pb2 as _embedded_proto_options_pb2
from kilight.protocol import VersionInfo_pb2 as _VersionInfo_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SystemInfo(_message.Message):
    __slots__ = ("hardwareId", "model", "manufacturer", "firmwareVersion", "hardwareVersion")
    HARDWAREID_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    FIRMWAREVERSION_FIELD_NUMBER: _ClassVar[int]
    HARDWAREVERSION_FIELD_NUMBER: _ClassVar[int]
    hardwareId: str
    model: str
    manufacturer: str
    firmwareVersion: _VersionInfo_pb2.VersionInfo
    hardwareVersion: _VersionInfo_pb2.VersionInfo
    def __init__(self, hardwareId: _Optional[str] = ..., model: _Optional[str] = ..., manufacturer: _Optional[str] = ..., firmwareVersion: _Optional[_Union[_VersionInfo_pb2.VersionInfo, _Mapping]] = ..., hardwareVersion: _Optional[_Union[_VersionInfo_pb2.VersionInfo, _Mapping]] = ...) -> None: ...
