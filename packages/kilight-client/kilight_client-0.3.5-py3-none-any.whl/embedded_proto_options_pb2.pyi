from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor
OPTIONS_FIELD_NUMBER: _ClassVar[int]
options: _descriptor.FieldDescriptor

class Options(_message.Message):
    __slots__ = ("maxLength",)
    MAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    maxLength: int
    def __init__(self, maxLength: _Optional[int] = ...) -> None: ...
