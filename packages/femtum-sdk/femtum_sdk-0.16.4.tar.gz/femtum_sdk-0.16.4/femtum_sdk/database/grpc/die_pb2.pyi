import femtum_sdk.database.grpc.tag_pb2 as _tag_pb2
import femtum_sdk.database.grpc.reticle_pb2 as _reticle_pb2
import femtum_sdk.database.grpc.wafer_pb2 as _wafer_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Die(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Tags", "Reticle", "Wafer")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    RETICLE_FIELD_NUMBER: _ClassVar[int]
    WAFER_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    Reticle: _reticle_pb2.Reticle
    Wafer: _wafer_pb2.Wafer
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ..., Reticle: _Optional[_Union[_reticle_pb2.Reticle, _Mapping]] = ..., Wafer: _Optional[_Union[_wafer_pb2.Wafer, _Mapping]] = ...) -> None: ...

class UpdateDieRequest(_message.Message):
    __slots__ = ("Id", "Name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    Id: str
    Name: str
    def __init__(self, Id: _Optional[str] = ..., Name: _Optional[str] = ...) -> None: ...

class DiesFilterRequest(_message.Message):
    __slots__ = ("Name", "ReticleId", "Tags")
    NAME_FIELD_NUMBER: _ClassVar[int]
    RETICLEID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    Name: str
    ReticleId: str
    Tags: _containers.RepeatedCompositeFieldContainer[_tag_pb2.Tag]
    def __init__(self, Name: _Optional[str] = ..., ReticleId: _Optional[str] = ..., Tags: _Optional[_Iterable[_Union[_tag_pb2.Tag, _Mapping]]] = ...) -> None: ...

class ListByPageDiesRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize", "Filters")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    Filters: DiesFilterRequest
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ..., Filters: _Optional[_Union[DiesFilterRequest, _Mapping]] = ...) -> None: ...

class DiesPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[Die]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[Die, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class FindDieByIdRequest(_message.Message):
    __slots__ = ("Id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    Id: str
    def __init__(self, Id: _Optional[str] = ...) -> None: ...

class OptionalDie(_message.Message):
    __slots__ = ("Die",)
    DIE_FIELD_NUMBER: _ClassVar[int]
    Die: Die
    def __init__(self, Die: _Optional[_Union[Die, _Mapping]] = ...) -> None: ...
