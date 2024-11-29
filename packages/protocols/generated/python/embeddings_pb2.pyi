from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateEmbeddingsRequest(_message.Message):
    __slots__ = ("sentences",)
    SENTENCES_FIELD_NUMBER: _ClassVar[int]
    sentences: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, sentences: _Optional[_Iterable[str]] = ...) -> None: ...

class GenerateEmbeddingsResponse(_message.Message):
    __slots__ = ("embeddings",)
    class Embedding(_message.Message):
        __slots__ = ("values",)
        VALUES_FIELD_NUMBER: _ClassVar[int]
        values: _containers.RepeatedScalarFieldContainer[float]
        def __init__(self, values: _Optional[_Iterable[float]] = ...) -> None: ...
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    embeddings: _containers.RepeatedCompositeFieldContainer[GenerateEmbeddingsResponse.Embedding]
    def __init__(self, embeddings: _Optional[_Iterable[_Union[GenerateEmbeddingsResponse.Embedding, _Mapping]]] = ...) -> None: ...
