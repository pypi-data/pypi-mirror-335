from kilight.protocol import GetData_pb2 as _GetData_pb2
from kilight.protocol import WriteOutput_pb2 as _WriteOutput_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ("getData", "writeOutput")
    GETDATA_FIELD_NUMBER: _ClassVar[int]
    WRITEOUTPUT_FIELD_NUMBER: _ClassVar[int]
    getData: _GetData_pb2.GetData
    writeOutput: _WriteOutput_pb2.WriteOutput
    def __init__(self, getData: _Optional[_Union[_GetData_pb2.GetData, str]] = ..., writeOutput: _Optional[_Union[_WriteOutput_pb2.WriteOutput, _Mapping]] = ...) -> None: ...
