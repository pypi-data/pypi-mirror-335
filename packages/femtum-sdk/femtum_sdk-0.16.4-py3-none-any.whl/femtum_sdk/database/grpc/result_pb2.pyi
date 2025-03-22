import femtum_sdk.database.grpc.tag_pb2 as _tag_pb2
import femtum_sdk.database.grpc.wafer_pb2 as _wafer_pb2
import femtum_sdk.database.grpc.reticle_pb2 as _reticle_pb2
import femtum_sdk.database.grpc.die_pb2 as _die_pb2
import femtum_sdk.database.grpc.circuit_pb2 as _circuit_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ComponentPath(_message.Message):
    __slots__ = ("Wafer", "Reticle", "Die", "Circuit")
    WAFER_FIELD_NUMBER: _ClassVar[int]
    RETICLE_FIELD_NUMBER: _ClassVar[int]
    DIE_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    Wafer: str
    Reticle: str
    Die: str
    Circuit: str
    def __init__(self, Wafer: _Optional[str] = ..., Reticle: _Optional[str] = ..., Die: _Optional[str] = ..., Circuit: _Optional[str] = ...) -> None: ...

class Result(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Type", "Tags", "Wafer", "Reticle", "Die", "Circuit", "DataJson")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    WAFER_FIELD_NUMBER: _ClassVar[int]
    RETICLE_FIELD_NUMBER: _ClassVar[int]
    DIE_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    DATAJSON_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Type: str
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    Wafer: _wafer_pb2.Wafer
    Reticle: _reticle_pb2.Reticle
    Die: _die_pb2.Die
    Circuit: _circuit_pb2.Circuit
    DataJson: str
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Type: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ..., Wafer: _Optional[_Union[_wafer_pb2.Wafer, _Mapping]] = ..., Reticle: _Optional[_Union[_reticle_pb2.Reticle, _Mapping]] = ..., Die: _Optional[_Union[_die_pb2.Die, _Mapping]] = ..., Circuit: _Optional[_Union[_circuit_pb2.Circuit, _Mapping]] = ..., DataJson: _Optional[str] = ...) -> None: ...

class OptionalSpectrumResult(_message.Message):
    __slots__ = ("Result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    Result: SpectrumResult
    def __init__(self, Result: _Optional[_Union[SpectrumResult, _Mapping]] = ...) -> None: ...

class OptionalSingleNumberResult(_message.Message):
    __slots__ = ("Result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    Result: SingleNumberResult
    def __init__(self, Result: _Optional[_Union[SingleNumberResult, _Mapping]] = ...) -> None: ...

class SingleNumberResult(_message.Message):
    __slots__ = ("Id", "data", "Name", "Path", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    data: SingleNumberData
    Name: str
    Path: ComponentPath
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Id: _Optional[str] = ..., data: _Optional[_Union[SingleNumberData, _Mapping]] = ..., Name: _Optional[str] = ..., Path: _Optional[_Union[ComponentPath, _Mapping]] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...

class SingleNumberData(_message.Message):
    __slots__ = ("Value", "Unit")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    Value: float
    Unit: str
    def __init__(self, Value: _Optional[float] = ..., Unit: _Optional[str] = ...) -> None: ...

class ResultsFilterRequest(_message.Message):
    __slots__ = ("ResultName", "WaferName", "ReticleName", "DieName", "CircuitName", "Tags", "WaferId", "ReticleId", "DieId", "CircuitId", "Type", "ProcessedCircuitId")
    RESULTNAME_FIELD_NUMBER: _ClassVar[int]
    WAFERNAME_FIELD_NUMBER: _ClassVar[int]
    RETICLENAME_FIELD_NUMBER: _ClassVar[int]
    DIENAME_FIELD_NUMBER: _ClassVar[int]
    CIRCUITNAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    WAFERID_FIELD_NUMBER: _ClassVar[int]
    RETICLEID_FIELD_NUMBER: _ClassVar[int]
    DIEID_FIELD_NUMBER: _ClassVar[int]
    CIRCUITID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROCESSEDCIRCUITID_FIELD_NUMBER: _ClassVar[int]
    ResultName: str
    WaferName: str
    ReticleName: str
    DieName: str
    CircuitName: str
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    WaferId: str
    ReticleId: str
    DieId: str
    CircuitId: str
    Type: str
    ProcessedCircuitId: str
    def __init__(self, ResultName: _Optional[str] = ..., WaferName: _Optional[str] = ..., ReticleName: _Optional[str] = ..., DieName: _Optional[str] = ..., CircuitName: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ..., WaferId: _Optional[str] = ..., ReticleId: _Optional[str] = ..., DieId: _Optional[str] = ..., CircuitId: _Optional[str] = ..., Type: _Optional[str] = ..., ProcessedCircuitId: _Optional[str] = ...) -> None: ...

class ListByPageResultsRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters", "IncludeData")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    INCLUDEDATA_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: ResultsFilterRequest
    IncludeData: bool
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[ResultsFilterRequest, _Mapping]] = ..., IncludeData: bool = ...) -> None: ...

class ResultsPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[Result]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[Result, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class FindResultByIdRequest(_message.Message):
    __slots__ = ("Id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    Id: str
    def __init__(self, Id: _Optional[str] = ...) -> None: ...

class OptionalSingleResult(_message.Message):
    __slots__ = ("Result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    Result: Result
    def __init__(self, Result: _Optional[_Union[Result, _Mapping]] = ...) -> None: ...

class FindResultByRequest(_message.Message):
    __slots__ = ("Path", "ResultName", "ShotNumber")
    PATH_FIELD_NUMBER: _ClassVar[int]
    RESULTNAME_FIELD_NUMBER: _ClassVar[int]
    SHOTNUMBER_FIELD_NUMBER: _ClassVar[int]
    Path: ComponentPath
    ResultName: str
    ShotNumber: int
    def __init__(self, Path: _Optional[_Union[ComponentPath, _Mapping]] = ..., ResultName: _Optional[str] = ..., ShotNumber: _Optional[int] = ...) -> None: ...

class StoreSingleNumberRequest(_message.Message):
    __slots__ = ("Value", "Unit", "Name", "Path", "ShotNumber", "Tags")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    SHOTNUMBER_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Value: float
    Unit: str
    Name: str
    Path: ComponentPath
    ShotNumber: int
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Value: _Optional[float] = ..., Unit: _Optional[str] = ..., Name: _Optional[str] = ..., Path: _Optional[_Union[ComponentPath, _Mapping]] = ..., ShotNumber: _Optional[int] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...

class BatchDeleteResultRequest(_message.Message):
    __slots__ = ("Ids",)
    IDS_FIELD_NUMBER: _ClassVar[int]
    Ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, Ids: _Optional[_Iterable[str]] = ...) -> None: ...

class ResultsArray(_message.Message):
    __slots__ = ("Items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[Result]
    def __init__(self, Items: _Optional[_Iterable[_Union[Result, _Mapping]]] = ...) -> None: ...

class StoreSpectrumResultRequest(_message.Message):
    __slots__ = ("Path", "Data", "Name", "Tags")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Path: ComponentPath
    Data: SpectrumData
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Path: _Optional[_Union[ComponentPath, _Mapping]] = ..., Data: _Optional[_Union[SpectrumData, _Mapping]] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...

class StoreSpectrumShotResultRequest(_message.Message):
    __slots__ = ("Path", "Data", "ShotNumber", "Name", "Tags")
    PATH_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SHOTNUMBER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Path: ComponentPath
    Data: SpectrumData
    ShotNumber: int
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Path: _Optional[_Union[ComponentPath, _Mapping]] = ..., Data: _Optional[_Union[SpectrumData, _Mapping]] = ..., ShotNumber: _Optional[int] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...

class SpectrumResult(_message.Message):
    __slots__ = ("Id", "Data", "Name", "Path", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    Data: SpectrumData
    Name: str
    Path: ComponentPath
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Id: _Optional[str] = ..., Data: _Optional[_Union[SpectrumData, _Mapping]] = ..., Name: _Optional[str] = ..., Path: _Optional[_Union[ComponentPath, _Mapping]] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...

class SpectrumData(_message.Message):
    __slots__ = ("WavelengthsArray", "PowersArray")
    WAVELENGTHSARRAY_FIELD_NUMBER: _ClassVar[int]
    POWERSARRAY_FIELD_NUMBER: _ClassVar[int]
    WavelengthsArray: _containers.RepeatedScalarFieldContainer[float]
    PowersArray: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, WavelengthsArray: _Optional[_Iterable[float]] = ..., PowersArray: _Optional[_Iterable[float]] = ...) -> None: ...
