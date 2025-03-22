from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Function(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "Version", "Language", "Author", "Entrypoint")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    ENTRYPOINT_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    Version: str
    Language: str
    Author: str
    Entrypoint: str
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., Version: _Optional[str] = ..., Language: _Optional[str] = ..., Author: _Optional[str] = ..., Entrypoint: _Optional[str] = ...) -> None: ...

class UpdateFunctionRequest(_message.Message):
    __slots__ = ("Id", "Entrypoint")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENTRYPOINT_FIELD_NUMBER: _ClassVar[int]
    Id: str
    Entrypoint: str
    def __init__(self, Id: _Optional[str] = ..., Entrypoint: _Optional[str] = ...) -> None: ...

class ListByPageFunctionRequest(_message.Message):
    __slots__ = ("PageNumber", "PageSize")
    PAGENUMBER_FIELD_NUMBER: _ClassVar[int]
    PAGESIZE_FIELD_NUMBER: _ClassVar[int]
    PageNumber: int
    PageSize: int
    def __init__(self, PageNumber: _Optional[int] = ..., PageSize: _Optional[int] = ...) -> None: ...

class FunctionsPage(_message.Message):
    __slots__ = ("Items", "Total", "Index", "Size")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    Items: _containers.RepeatedCompositeFieldContainer[Function]
    Total: int
    Index: int
    Size: int
    def __init__(self, Items: _Optional[_Iterable[_Union[Function, _Mapping]]] = ..., Total: _Optional[int] = ..., Index: _Optional[int] = ..., Size: _Optional[int] = ...) -> None: ...

class FindFunctionByIdRequest(_message.Message):
    __slots__ = ("Id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    Id: str
    def __init__(self, Id: _Optional[str] = ...) -> None: ...

class OptionalFunction(_message.Message):
    __slots__ = ("Function",)
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    Function: Function
    def __init__(self, Function: _Optional[_Union[Function, _Mapping]] = ...) -> None: ...
