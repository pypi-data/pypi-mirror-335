from google.protobuf import timestamp_pb2 as _timestamp_pb2
import LocationFix_pb2 as _LocationFix_pb2
import Vessel_pb2 as _Vessel_pb2
import SeaMark_pb2 as _SeaMark_pb2
import Navigation_pb2 as _Navigation_pb2
import GeoJSON_pb2 as _GeoJSON_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Targets(_message.Message):
    __slots__ = ("timestamp", "targets")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    targets: _containers.RepeatedCompositeFieldContainer[Target]
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., targets: _Optional[_Iterable[_Union[Target, _Mapping]]] = ...) -> None: ...

class Target(_message.Message):
    __slots__ = ("timestamp", "data_source", "description", "position", "location", "geojson", "speed_through_water", "trajectory_over_ground", "rate_of_turn", "heading", "collision_monitoring", "navigation_status", "json_str")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    GEOJSON_FIELD_NUMBER: _ClassVar[int]
    SPEED_THROUGH_WATER_FIELD_NUMBER: _ClassVar[int]
    TRAJECTORY_OVER_GROUND_FIELD_NUMBER: _ClassVar[int]
    RATE_OF_TURN_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    COLLISION_MONITORING_FIELD_NUMBER: _ClassVar[int]
    NAVIGATION_STATUS_FIELD_NUMBER: _ClassVar[int]
    JSON_STR_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    data_source: TargetDataSource
    description: TargetDescription
    position: _LocationFix_pb2.PositionFix
    location: _LocationFix_pb2.LocationFix
    geojson: _GeoJSON_pb2.GeoJSON
    speed_through_water: _Navigation_pb2.SpeedThroughWater
    trajectory_over_ground: _Navigation_pb2.TrajectoryOverGround
    rate_of_turn: _Navigation_pb2.RateOfTurn
    heading: _Navigation_pb2.Heading
    collision_monitoring: _Navigation_pb2.CollisionMonitoring
    navigation_status: _Navigation_pb2.NavigationStatus
    json_str: str
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., data_source: _Optional[_Union[TargetDataSource, _Mapping]] = ..., description: _Optional[_Union[TargetDescription, _Mapping]] = ..., position: _Optional[_Union[_LocationFix_pb2.PositionFix, _Mapping]] = ..., location: _Optional[_Union[_LocationFix_pb2.LocationFix, _Mapping]] = ..., geojson: _Optional[_Union[_GeoJSON_pb2.GeoJSON, _Mapping]] = ..., speed_through_water: _Optional[_Union[_Navigation_pb2.SpeedThroughWater, _Mapping]] = ..., trajectory_over_ground: _Optional[_Union[_Navigation_pb2.TrajectoryOverGround, _Mapping]] = ..., rate_of_turn: _Optional[_Union[_Navigation_pb2.RateOfTurn, _Mapping]] = ..., heading: _Optional[_Union[_Navigation_pb2.Heading, _Mapping]] = ..., collision_monitoring: _Optional[_Union[_Navigation_pb2.CollisionMonitoring, _Mapping]] = ..., navigation_status: _Optional[_Union[_Navigation_pb2.NavigationStatus, _Mapping]] = ..., json_str: _Optional[str] = ...) -> None: ...

class TargetDescription(_message.Message):
    __slots__ = ("timestamp", "target_type", "vessel", "sea_mark", "target_json_str")
    class TargetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[TargetDescription.TargetType]
        VESSEL: _ClassVar[TargetDescription.TargetType]
        SEAMARK: _ClassVar[TargetDescription.TargetType]
    UNKNOWN: TargetDescription.TargetType
    VESSEL: TargetDescription.TargetType
    SEAMARK: TargetDescription.TargetType
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TARGET_TYPE_FIELD_NUMBER: _ClassVar[int]
    VESSEL_FIELD_NUMBER: _ClassVar[int]
    SEA_MARK_FIELD_NUMBER: _ClassVar[int]
    TARGET_JSON_STR_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    target_type: TargetDescription.TargetType
    vessel: _Vessel_pb2.Vessel
    sea_mark: _SeaMark_pb2.SeaMark
    target_json_str: str
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., target_type: _Optional[_Union[TargetDescription.TargetType, str]] = ..., vessel: _Optional[_Union[_Vessel_pb2.Vessel, _Mapping]] = ..., sea_mark: _Optional[_Union[_SeaMark_pb2.SeaMark, _Mapping]] = ..., target_json_str: _Optional[str] = ...) -> None: ...

class TargetDataSource(_message.Message):
    __slots__ = ("sources_type", "source_name", "source_json_str")
    class Source(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OTHER: _ClassVar[TargetDataSource.Source]
        AIS_RADIO: _ClassVar[TargetDataSource.Source]
        AIS_PROVIDER: _ClassVar[TargetDataSource.Source]
        RADAR_MARINE: _ClassVar[TargetDataSource.Source]
        RADAR_VEHICLE: _ClassVar[TargetDataSource.Source]
        LIDAR: _ClassVar[TargetDataSource.Source]
        CAMERA_RBG: _ClassVar[TargetDataSource.Source]
        CAMERA_MONO: _ClassVar[TargetDataSource.Source]
        CAMERA_IR: _ClassVar[TargetDataSource.Source]
        SIMULATION: _ClassVar[TargetDataSource.Source]
    OTHER: TargetDataSource.Source
    AIS_RADIO: TargetDataSource.Source
    AIS_PROVIDER: TargetDataSource.Source
    RADAR_MARINE: TargetDataSource.Source
    RADAR_VEHICLE: TargetDataSource.Source
    LIDAR: TargetDataSource.Source
    CAMERA_RBG: TargetDataSource.Source
    CAMERA_MONO: TargetDataSource.Source
    CAMERA_IR: TargetDataSource.Source
    SIMULATION: TargetDataSource.Source
    SOURCES_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    SOURCE_JSON_STR_FIELD_NUMBER: _ClassVar[int]
    sources_type: _containers.RepeatedScalarFieldContainer[TargetDataSource.Source]
    source_name: str
    source_json_str: str
    def __init__(self, sources_type: _Optional[_Iterable[_Union[TargetDataSource.Source, str]]] = ..., source_name: _Optional[str] = ..., source_json_str: _Optional[str] = ...) -> None: ...
