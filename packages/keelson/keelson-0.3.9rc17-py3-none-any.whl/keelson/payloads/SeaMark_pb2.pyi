from google.protobuf import timestamp_pb2 as _timestamp_pb2
import LocationFix_pb2 as _LocationFix_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SeaMarks(_message.Message):
    __slots__ = ("timestamp", "sea_marks")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SEA_MARKS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    sea_marks: _containers.RepeatedCompositeFieldContainer[SeaMark]
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., sea_marks: _Optional[_Iterable[_Union[SeaMark, _Mapping]]] = ...) -> None: ...

class SeaMark(_message.Message):
    __slots__ = ("timestamp", "position", "object_information_json_str")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    OBJECT_INFORMATION_JSON_STR_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    position: _LocationFix_pb2.PositionFix
    object_information_json_str: str
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., position: _Optional[_Union[_LocationFix_pb2.PositionFix, _Mapping]] = ..., object_information_json_str: _Optional[str] = ...) -> None: ...
