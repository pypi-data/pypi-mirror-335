from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FanState(_message.Message):
    __slots__ = ("rpm", "outputPerThou")
    RPM_FIELD_NUMBER: _ClassVar[int]
    OUTPUTPERTHOU_FIELD_NUMBER: _ClassVar[int]
    rpm: int
    outputPerThou: int
    def __init__(self, rpm: _Optional[int] = ..., outputPerThou: _Optional[int] = ...) -> None: ...
