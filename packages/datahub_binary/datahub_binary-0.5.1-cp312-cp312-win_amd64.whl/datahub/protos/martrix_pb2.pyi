from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FinancialMatrix(_message.Message):
    __slots__ = ("msg_type", "msg_sequence", "trade_time", "last_timestamp", "instrument_ids", "cols", "data_matrix")
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    MSG_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TRADE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    INSTRUMENT_IDS_FIELD_NUMBER: _ClassVar[int]
    COLS_FIELD_NUMBER: _ClassVar[int]
    DATA_MATRIX_FIELD_NUMBER: _ClassVar[int]
    msg_type: int
    msg_sequence: int
    trade_time: int
    last_timestamp: int
    instrument_ids: _containers.RepeatedScalarFieldContainer[str]
    cols: _containers.RepeatedScalarFieldContainer[str]
    data_matrix: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, msg_type: _Optional[int] = ..., msg_sequence: _Optional[int] = ..., trade_time: _Optional[int] = ..., last_timestamp: _Optional[int] = ..., instrument_ids: _Optional[_Iterable[str]] = ..., cols: _Optional[_Iterable[str]] = ..., data_matrix: _Optional[_Iterable[int]] = ...) -> None: ...
