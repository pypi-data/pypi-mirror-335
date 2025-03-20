from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimestampedBytes(_message.Message):
    __slots__ = ("timestamp", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: bytes
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[bytes] = ...) -> None: ...

class TimestampedDouble(_message.Message):
    __slots__ = ("timestamp", "value", "unit")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: float
    unit: MeasurementUnit
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[float] = ..., unit: _Optional[_Union[MeasurementUnit, _Mapping]] = ...) -> None: ...

class TimestampedFloat(_message.Message):
    __slots__ = ("timestamp", "value", "unit")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: float
    unit: MeasurementUnit
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[float] = ..., unit: _Optional[_Union[MeasurementUnit, _Mapping]] = ...) -> None: ...

class TimestampedInt(_message.Message):
    __slots__ = ("timestamp", "value", "unit")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: int
    unit: MeasurementUnit
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[int] = ..., unit: _Optional[_Union[MeasurementUnit, _Mapping]] = ...) -> None: ...

class TimestampedString(_message.Message):
    __slots__ = ("timestamp", "value", "unit")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: str
    unit: MeasurementUnit
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[str] = ..., unit: _Optional[_Union[MeasurementUnit, _Mapping]] = ...) -> None: ...

class MeasurementUnit(_message.Message):
    __slots__ = ("unit",)
    class Unit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[MeasurementUnit.Unit]
        DEGREES: _ClassVar[MeasurementUnit.Unit]
        FEET: _ClassVar[MeasurementUnit.Unit]
        KILOMETERS: _ClassVar[MeasurementUnit.Unit]
        METERS: _ClassVar[MeasurementUnit.Unit]
        MILES: _ClassVar[MeasurementUnit.Unit]
        NAUTICAL_MILES: _ClassVar[MeasurementUnit.Unit]
        YARDS: _ClassVar[MeasurementUnit.Unit]
        AMPERES: _ClassVar[MeasurementUnit.Unit]
        JOULES: _ClassVar[MeasurementUnit.Unit]
        LUMENS: _ClassVar[MeasurementUnit.Unit]
        LUX: _ClassVar[MeasurementUnit.Unit]
        NEWTONS: _ClassVar[MeasurementUnit.Unit]
        OHMS: _ClassVar[MeasurementUnit.Unit]
        VOLTS: _ClassVar[MeasurementUnit.Unit]
        WATTS: _ClassVar[MeasurementUnit.Unit]
        HERTZ: _ClassVar[MeasurementUnit.Unit]
        GRAMS: _ClassVar[MeasurementUnit.Unit]
        OUNCES: _ClassVar[MeasurementUnit.Unit]
        POUNDS: _ClassVar[MeasurementUnit.Unit]
        HECTOPASCALS: _ClassVar[MeasurementUnit.Unit]
        INCHES_OF_MERCURY: _ClassVar[MeasurementUnit.Unit]
        MILLIBARS: _ClassVar[MeasurementUnit.Unit]
        PASCALS: _ClassVar[MeasurementUnit.Unit]
        KILOMETERS_PER_HOUR: _ClassVar[MeasurementUnit.Unit]
        KNOTS: _ClassVar[MeasurementUnit.Unit]
        METERS_PER_SECOND: _ClassVar[MeasurementUnit.Unit]
        CELSIUS: _ClassVar[MeasurementUnit.Unit]
        FAHRENHEIT: _ClassVar[MeasurementUnit.Unit]
        KELVIN: _ClassVar[MeasurementUnit.Unit]
        GALLONS: _ClassVar[MeasurementUnit.Unit]
        LITERS: _ClassVar[MeasurementUnit.Unit]
        CANDELA: _ClassVar[MeasurementUnit.Unit]
        DECIBELS: _ClassVar[MeasurementUnit.Unit]
        PERCENTAGE: _ClassVar[MeasurementUnit.Unit]
        RPM: _ClassVar[MeasurementUnit.Unit]
    UNKNOWN: MeasurementUnit.Unit
    DEGREES: MeasurementUnit.Unit
    FEET: MeasurementUnit.Unit
    KILOMETERS: MeasurementUnit.Unit
    METERS: MeasurementUnit.Unit
    MILES: MeasurementUnit.Unit
    NAUTICAL_MILES: MeasurementUnit.Unit
    YARDS: MeasurementUnit.Unit
    AMPERES: MeasurementUnit.Unit
    JOULES: MeasurementUnit.Unit
    LUMENS: MeasurementUnit.Unit
    LUX: MeasurementUnit.Unit
    NEWTONS: MeasurementUnit.Unit
    OHMS: MeasurementUnit.Unit
    VOLTS: MeasurementUnit.Unit
    WATTS: MeasurementUnit.Unit
    HERTZ: MeasurementUnit.Unit
    GRAMS: MeasurementUnit.Unit
    OUNCES: MeasurementUnit.Unit
    POUNDS: MeasurementUnit.Unit
    HECTOPASCALS: MeasurementUnit.Unit
    INCHES_OF_MERCURY: MeasurementUnit.Unit
    MILLIBARS: MeasurementUnit.Unit
    PASCALS: MeasurementUnit.Unit
    KILOMETERS_PER_HOUR: MeasurementUnit.Unit
    KNOTS: MeasurementUnit.Unit
    METERS_PER_SECOND: MeasurementUnit.Unit
    CELSIUS: MeasurementUnit.Unit
    FAHRENHEIT: MeasurementUnit.Unit
    KELVIN: MeasurementUnit.Unit
    GALLONS: MeasurementUnit.Unit
    LITERS: MeasurementUnit.Unit
    CANDELA: MeasurementUnit.Unit
    DECIBELS: MeasurementUnit.Unit
    PERCENTAGE: MeasurementUnit.Unit
    RPM: MeasurementUnit.Unit
    UNIT_FIELD_NUMBER: _ClassVar[int]
    unit: MeasurementUnit.Unit
    def __init__(self, unit: _Optional[_Union[MeasurementUnit.Unit, str]] = ...) -> None: ...
