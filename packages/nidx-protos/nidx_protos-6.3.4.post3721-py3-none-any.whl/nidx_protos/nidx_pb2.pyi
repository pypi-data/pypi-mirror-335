from nucliadb_protos import nodereader_pb2 as _nodereader_pb2
from nucliadb_protos import noderesources_pb2 as _noderesources_pb2
from nucliadb_protos import utils_pb2 as _utils_pb2
from nucliadb_protos import nodewriter_pb2 as _nodewriter_pb2
from nucliadb_protos import noderesources_pb2 as _noderesources_pb2_1
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Notification(_message.Message):
    __slots__ = ("uuid", "kbid", "seqid", "action")
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COMMIT: _ClassVar[Notification.Action]
        ABORT: _ClassVar[Notification.Action]
        INDEXED: _ClassVar[Notification.Action]
    COMMIT: Notification.Action
    ABORT: Notification.Action
    INDEXED: Notification.Action
    UUID_FIELD_NUMBER: _ClassVar[int]
    KBID_FIELD_NUMBER: _ClassVar[int]
    SEQID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    kbid: str
    seqid: int
    action: Notification.Action
    def __init__(self, uuid: _Optional[str] = ..., kbid: _Optional[str] = ..., seqid: _Optional[int] = ..., action: _Optional[_Union[Notification.Action, str]] = ...) -> None: ...
