from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Ping(_message.Message):
    __slots__ = ("msg_type", "msg_sequence")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    msg_sequence: int
    def __init__(self, msg_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ...) -> None: ...

class Pong(_message.Message):
    __slots__ = ("msg_type", "msg_sequence")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    msg_sequence: int
    def __init__(self, msg_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ...) -> None: ...

class ManagerNotLogin(_message.Message):
    __slots__ = ("msg_type", "last_timestamp")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    last_timestamp: int
    def __init__(self, msg_type: _Optional[int] = ..., last_timestamp: _Optional[int] = ...) -> None: ...

class ManagerErrorMsg(_message.Message):
    __slots__ = ("msg_type", "error_msg", "last_timestamp", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    error_msg: str
    last_timestamp: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., error_msg: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class LoginReq(_message.Message):
    __slots__ = ("msg_type", "user_id", "passwd", "last_timestamp", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PASSWD_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    user_id: str
    passwd: str
    last_timestamp: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., user_id: _Optional[str] = ..., passwd: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...

class LoginRsp(_message.Message):
    __slots__ = ("msg_type", "is_succ", "error_msg", "last_timestamp", "request_id")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_SUCC_FIELD_NUMBER: _ClassVar[int]
    ERROR_MSG_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    is_succ: bool
    error_msg: str
    last_timestamp: int
    request_id: str
    def __init__(self, msg_type: _Optional[int] = ..., is_succ: bool = ..., error_msg: _Optional[str] = ..., last_timestamp: _Optional[int] = ..., request_id: _Optional[str] = ...) -> None: ...
