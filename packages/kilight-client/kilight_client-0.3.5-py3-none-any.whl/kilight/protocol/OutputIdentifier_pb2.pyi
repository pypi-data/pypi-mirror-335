from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class OutputIdentifier(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Invalid: _ClassVar[OutputIdentifier]
    OutputA: _ClassVar[OutputIdentifier]
    OutputB: _ClassVar[OutputIdentifier]
Invalid: OutputIdentifier
OutputA: OutputIdentifier
OutputB: OutputIdentifier
