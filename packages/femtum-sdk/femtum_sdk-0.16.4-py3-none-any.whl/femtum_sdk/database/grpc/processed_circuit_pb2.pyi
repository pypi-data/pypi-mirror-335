import femtum_sdk.database.grpc.tag_pb2 as _tag_pb2
import femtum_sdk.database.grpc.wafer_pb2 as _wafer_pb2
import femtum_sdk.database.grpc.reticle_pb2 as _reticle_pb2
import femtum_sdk.database.grpc.die_pb2 as _die_pb2
import femtum_sdk.database.grpc.circuit_pb2 as _circuit_pb2
import femtum_sdk.database.grpc.result_pb2 as _result_pb2
import femtum_sdk.database.grpc.attachment_pb2 as _attachment_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProcessedCircuit(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Wafer", "Reticle", "Die", "Circuit", "Results", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    WAFER_FIELD_NUMBER: _ClassVar[int]
    RETICLE_FIELD_NUMBER: _ClassVar[int]
    DIE_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Wafer: _wafer_pb2.Wafer
    Reticle: _reticle_pb2.Reticle
    Die: _die_pb2.Die
    Circuit: _circuit_pb2.Circuit
    Results: _containers.RepeatedCompositeFieldContainer[_result_pb2.Result]
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Wafer: _Optional[_Union[_wafer_pb2.Wafer, _Mapping]] = ..., Reticle: _Optional[_Union[_reticle_pb2.Reticle, _Mapping]] = ..., Die: _Optional[_Union[_die_pb2.Die, _Mapping]] = ..., Circuit: _Optional[_Union[_circuit_pb2.Circuit, _Mapping]] = ..., Results: _Optional[_Iterable[_Union[_result_pb2.Result, _Mapping]]] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...

class ProcessedCircuitFilterRequest(_message.Message):
    __slots__ = ("WaferId", "ReticleId", "DieId", "CircuitId", "WaferName", "ReticleName", "DieName", "CircuitName")
    WAFERID_FIELD_NUMBER: _ClassVar[int]
    RETICLEID_FIELD_NUMBER: _ClassVar[int]
    DIEID_FIELD_NUMBER: _ClassVar[int]
    CIRCUITID_FIELD_NUMBER: _ClassVar[int]
    WAFERNAME_FIELD_NUMBER: _ClassVar[int]
    RETICLENAME_FIELD_NUMBER: _ClassVar[int]
    DIENAME_FIELD_NUMBER: _ClassVar[int]
    CIRCUITNAME_FIELD_NUMBER: _ClassVar[int]
    WaferId: str
    ReticleId: str
    DieId: str
    CircuitId: str
    WaferName: str
    ReticleName: str
    DieName: str
    CircuitName: str
    def __init__(self, WaferId: _Optional[str] = ..., ReticleId: _Optional[str] = ..., DieId: _Optional[str] = ..., CircuitId: _Optional[str] = ..., WaferName: _Optional[str] = ..., ReticleName: _Optional[str] = ..., DieName: _Optional[str] = ..., CircuitName: _Optional[str] = ...) -> None: ...

class ListByPageProcessedCircuitRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: ProcessedCircuitFilterRequest
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[ProcessedCircuitFilterRequest, _Mapping]] = ...) -> None: ...

class ProcessedCircuitPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[ProcessedCircuit]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[ProcessedCircuit, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class FindProcessedCircuitByIdRequest(_message.Message):
    __slots__ = ("Id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    Id: str
    def __init__(self, Id: _Optional[str] = ...) -> None: ...

class OptionalProcessedCircuit(_message.Message):
    __slots__ = ("Circuit",)
    CIRCUIT_FIELD_NUMBER: _ClassVar[int]
    Circuit: ProcessedCircuit
    def __init__(self, Circuit: _Optional[_Union[ProcessedCircuit, _Mapping]] = ...) -> None: ...

class AddProcessedCircuitImageRequest(_message.Message):
    __slots__ = ("Id", "Attachment")
    ID_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    Id: str
    Attachment: _attachment_pb2.NewAttachment
    def __init__(self, Id: _Optional[str] = ..., Attachment: _Optional[_Union[_attachment_pb2.NewAttachment, _Mapping]] = ...) -> None: ...

class SetProcessedCircuitTagsRequest(_message.Message):
    __slots__ = ("Id", "Tags")
    ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Id: str
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Id: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...
