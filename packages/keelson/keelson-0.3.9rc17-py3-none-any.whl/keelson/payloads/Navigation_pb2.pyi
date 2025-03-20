from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SpeedThroughWater(_message.Message):
    __slots__ = ("timestamp", "speed_through_water_knots")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SPEED_THROUGH_WATER_KNOTS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    speed_through_water_knots: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., speed_through_water_knots: _Optional[float] = ...) -> None: ...

class TrajectoryOverGround(_message.Message):
    __slots__ = ("timestamp", "course_over_ground_degrees", "speed_over_ground_knots", "bow_speed_over_ground_knots", "stern_speed_over_ground_knots")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    COURSE_OVER_GROUND_DEGREES_FIELD_NUMBER: _ClassVar[int]
    SPEED_OVER_GROUND_KNOTS_FIELD_NUMBER: _ClassVar[int]
    BOW_SPEED_OVER_GROUND_KNOTS_FIELD_NUMBER: _ClassVar[int]
    STERN_SPEED_OVER_GROUND_KNOTS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    course_over_ground_degrees: float
    speed_over_ground_knots: float
    bow_speed_over_ground_knots: float
    stern_speed_over_ground_knots: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., course_over_ground_degrees: _Optional[float] = ..., speed_over_ground_knots: _Optional[float] = ..., bow_speed_over_ground_knots: _Optional[float] = ..., stern_speed_over_ground_knots: _Optional[float] = ...) -> None: ...

class RateOfTurn(_message.Message):
    __slots__ = ("timestamp", "rate_of_turn_degrees_per_minute")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RATE_OF_TURN_DEGREES_PER_MINUTE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    rate_of_turn_degrees_per_minute: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., rate_of_turn_degrees_per_minute: _Optional[float] = ...) -> None: ...

class Heading(_message.Message):
    __slots__ = ("timestamp", "heading_degrees")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    HEADING_DEGREES_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    heading_degrees: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., heading_degrees: _Optional[float] = ...) -> None: ...

class CommonReferencePoint(_message.Message):
    __slots__ = ("distance_to_bow_meters", "distance_to_stern_meters", "distance_to_port_meters", "distance_to_starboard_meters")
    DISTANCE_TO_BOW_METERS_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_TO_STERN_METERS_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_TO_PORT_METERS_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_TO_STARBOARD_METERS_FIELD_NUMBER: _ClassVar[int]
    distance_to_bow_meters: float
    distance_to_stern_meters: float
    distance_to_port_meters: float
    distance_to_starboard_meters: float
    def __init__(self, distance_to_bow_meters: _Optional[float] = ..., distance_to_stern_meters: _Optional[float] = ..., distance_to_port_meters: _Optional[float] = ..., distance_to_starboard_meters: _Optional[float] = ...) -> None: ...

class Sonar(_message.Message):
    __slots__ = ("timestamp", "depth_meters", "temperature_celsius", "salinity_ppt", "speed_of_sound_meters_per_second", "speed_through_water", "speed_over_ground")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DEPTH_METERS_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_CELSIUS_FIELD_NUMBER: _ClassVar[int]
    SALINITY_PPT_FIELD_NUMBER: _ClassVar[int]
    SPEED_OF_SOUND_METERS_PER_SECOND_FIELD_NUMBER: _ClassVar[int]
    SPEED_THROUGH_WATER_FIELD_NUMBER: _ClassVar[int]
    SPEED_OVER_GROUND_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    depth_meters: float
    temperature_celsius: float
    salinity_ppt: float
    speed_of_sound_meters_per_second: float
    speed_through_water: SpeedThroughWater
    speed_over_ground: TrajectoryOverGround
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., depth_meters: _Optional[float] = ..., temperature_celsius: _Optional[float] = ..., salinity_ppt: _Optional[float] = ..., speed_of_sound_meters_per_second: _Optional[float] = ..., speed_through_water: _Optional[_Union[SpeedThroughWater, _Mapping]] = ..., speed_over_ground: _Optional[_Union[TrajectoryOverGround, _Mapping]] = ...) -> None: ...

class CollisionMonitoring(_message.Message):
    __slots__ = ("timestamp", "cpa_metres", "tcpa_seconds", "bcr_metres", "bct_seconds", "bearing_north_degrees", "distance_metres")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CPA_METRES_FIELD_NUMBER: _ClassVar[int]
    TCPA_SECONDS_FIELD_NUMBER: _ClassVar[int]
    BCR_METRES_FIELD_NUMBER: _ClassVar[int]
    BCT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    BEARING_NORTH_DEGREES_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_METRES_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    cpa_metres: float
    tcpa_seconds: float
    bcr_metres: float
    bct_seconds: float
    bearing_north_degrees: float
    distance_metres: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cpa_metres: _Optional[float] = ..., tcpa_seconds: _Optional[float] = ..., bcr_metres: _Optional[float] = ..., bct_seconds: _Optional[float] = ..., bearing_north_degrees: _Optional[float] = ..., distance_metres: _Optional[float] = ...) -> None: ...

class SteeringAngle(_message.Message):
    __slots__ = ("timestamp", "rudder_angle_degrees")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RUDDER_ANGLE_DEGREES_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    rudder_angle_degrees: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., rudder_angle_degrees: _Optional[float] = ...) -> None: ...

class NavigationStatus(_message.Message):
    __slots__ = ("timestamp", "status")
    class NavigationStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[NavigationStatus.NavigationStatusType]
        UNDER_WAY: _ClassVar[NavigationStatus.NavigationStatusType]
        AT_ANCHOR: _ClassVar[NavigationStatus.NavigationStatusType]
        NOT_UNDER_COMMAND: _ClassVar[NavigationStatus.NavigationStatusType]
        RESTRICTED_MANEUVERABILITY: _ClassVar[NavigationStatus.NavigationStatusType]
        CONSTRAINED_BY_DRAUGHT: _ClassVar[NavigationStatus.NavigationStatusType]
        MOORED: _ClassVar[NavigationStatus.NavigationStatusType]
        AGROUND: _ClassVar[NavigationStatus.NavigationStatusType]
        ENGAGED_IN_FISHING: _ClassVar[NavigationStatus.NavigationStatusType]
        UNDER_WAY_SAILING: _ClassVar[NavigationStatus.NavigationStatusType]
        FUTURE_HSC: _ClassVar[NavigationStatus.NavigationStatusType]
        FUTURE_WIG: _ClassVar[NavigationStatus.NavigationStatusType]
        TOWING_ASTERN: _ClassVar[NavigationStatus.NavigationStatusType]
        PUSHING_AHEAD: _ClassVar[NavigationStatus.NavigationStatusType]
        RESERVED_FUTURE_USE: _ClassVar[NavigationStatus.NavigationStatusType]
        AIS_SART: _ClassVar[NavigationStatus.NavigationStatusType]
        UNDEFINED: _ClassVar[NavigationStatus.NavigationStatusType]
    UNKNOWN: NavigationStatus.NavigationStatusType
    UNDER_WAY: NavigationStatus.NavigationStatusType
    AT_ANCHOR: NavigationStatus.NavigationStatusType
    NOT_UNDER_COMMAND: NavigationStatus.NavigationStatusType
    RESTRICTED_MANEUVERABILITY: NavigationStatus.NavigationStatusType
    CONSTRAINED_BY_DRAUGHT: NavigationStatus.NavigationStatusType
    MOORED: NavigationStatus.NavigationStatusType
    AGROUND: NavigationStatus.NavigationStatusType
    ENGAGED_IN_FISHING: NavigationStatus.NavigationStatusType
    UNDER_WAY_SAILING: NavigationStatus.NavigationStatusType
    FUTURE_HSC: NavigationStatus.NavigationStatusType
    FUTURE_WIG: NavigationStatus.NavigationStatusType
    TOWING_ASTERN: NavigationStatus.NavigationStatusType
    PUSHING_AHEAD: NavigationStatus.NavigationStatusType
    RESERVED_FUTURE_USE: NavigationStatus.NavigationStatusType
    AIS_SART: NavigationStatus.NavigationStatusType
    UNDEFINED: NavigationStatus.NavigationStatusType
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    status: NavigationStatus.NavigationStatusType
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[NavigationStatus.NavigationStatusType, str]] = ...) -> None: ...
