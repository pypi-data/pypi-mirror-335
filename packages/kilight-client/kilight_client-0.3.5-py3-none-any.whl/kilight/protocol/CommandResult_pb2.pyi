from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandResult(_message.Message):
    __slots__ = ("result",)
    class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[CommandResult.Result]
        Error: _ClassVar[CommandResult.Result]
    OK: CommandResult.Result
    Error: CommandResult.Result
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: CommandResult.Result
    def __init__(self, result: _Optional[_Union[CommandResult.Result, str]] = ...) -> None: ...
