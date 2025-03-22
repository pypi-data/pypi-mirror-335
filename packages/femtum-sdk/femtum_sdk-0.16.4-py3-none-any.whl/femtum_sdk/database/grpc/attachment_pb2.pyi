from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NewAttachment(_message.Message):
    __slots__ = ("Name", "MimeType", "BlobData")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    BLOBDATA_FIELD_NUMBER: _ClassVar[int]
    Name: str
    MimeType: str
    BlobData: bytes
    def __init__(self, Name: _Optional[str] = ..., MimeType: _Optional[str] = ..., BlobData: _Optional[bytes] = ...) -> None: ...

class Attachment(_message.Message):
    __slots__ = ("Id", "CreatedAt", "UpdatedAt", "Name", "MimeType", "BlobData")
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIMETYPE_FIELD_NUMBER: _ClassVar[int]
    BLOBDATA_FIELD_NUMBER: _ClassVar[int]
    Id: str
    CreatedAt: str
    UpdatedAt: str
    Name: str
    MimeType: str
    BlobData: bytes
    def __init__(self, Id: _Optional[str] = ..., CreatedAt: _Optional[str] = ..., UpdatedAt: _Optional[str] = ..., Name: _Optional[str] = ..., MimeType: _Optional[str] = ..., BlobData: _Optional[bytes] = ...) -> None: ...

class OptionalAttachment(_message.Message):
    __slots__ = ("Attachment",)
    ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    Attachment: Attachment
    def __init__(self, Attachment: _Optional[_Union[Attachment, _Mapping]] = ...) -> None: ...

class AttachmentsArray(_message.Message):
    __slots__ = ("Attachments",)
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    Attachments: _containers.RepeatedCompositeFieldContainer[Attachment]
    def __init__(self, Attachments: _Optional[_Iterable[_Union[Attachment, _Mapping]]] = ...) -> None: ...

class DeleteAttachmentRequest(_message.Message):
    __slots__ = ("Id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    Id: str
    def __init__(self, Id: _Optional[str] = ...) -> None: ...
