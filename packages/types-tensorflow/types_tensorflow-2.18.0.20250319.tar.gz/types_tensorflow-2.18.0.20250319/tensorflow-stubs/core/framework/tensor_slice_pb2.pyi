"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
Protocol buffer representing slices of a tensor"""

import builtins
import collections.abc
import typing

import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.message

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

@typing.final
class TensorSliceProto(google.protobuf.message.Message):
    """Can only be interpreted if you know the corresponding TensorShape."""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing.final
    class Extent(google.protobuf.message.Message):
        """Extent of the slice in one dimension.
        Either both or no attributes must be set.  When no attribute is set
        means: All data in that dimension.
        """

        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        START_FIELD_NUMBER: builtins.int
        LENGTH_FIELD_NUMBER: builtins.int
        start: builtins.int
        """Start index of the slice, starting at 0."""
        length: builtins.int
        def __init__(
            self,
            *,
            start: builtins.int | None = ...,
            length: builtins.int | None = ...,
        ) -> None: ...
        def HasField(self, field_name: typing.Literal["has_length", b"has_length", "length", b"length"]) -> builtins.bool: ...
        def ClearField(self, field_name: typing.Literal["has_length", b"has_length", "length", b"length", "start", b"start"]) -> None: ...
        def WhichOneof(self, oneof_group: typing.Literal["has_length", b"has_length"]) -> typing.Literal["length"] | None: ...

    EXTENT_FIELD_NUMBER: builtins.int
    @property
    def extent(self) -> google.protobuf.internal.containers.RepeatedCompositeFieldContainer[global___TensorSliceProto.Extent]:
        """Extent of the slice in all tensor dimensions.

        Must have one entry for each of the dimension of the tensor that this
        slice belongs to.  The order of sizes is the same as the order of
        dimensions in the TensorShape.
        """

    def __init__(
        self,
        *,
        extent: collections.abc.Iterable[global___TensorSliceProto.Extent] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing.Literal["extent", b"extent"]) -> None: ...

global___TensorSliceProto = TensorSliceProto
