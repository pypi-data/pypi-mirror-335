"""
This file defines the types for type annotations.

These names aren't part of the module namespace, but they are used in the
annotations in the function signatures. The functions in the module are only
valid for inputs that match the given type annotations.
"""

from __future__ import annotations

__all__ = [
    "Array",
    "Device",
    "Dtype",
    "SupportsDLPack",
    "SupportsBufferProtocol",
    "PyCapsule",
]

import sys

from typing import (
    Any,
    TypedDict,
    TypeVar,
    Protocol,
)

from ._array_object import Array, _device
from ._dtypes import _DType
from ._info import __array_namespace_info__

_T_co = TypeVar("_T_co", covariant=True)

class NestedSequence(Protocol[_T_co]):
    def __getitem__(self, key: int, /) -> _T_co | NestedSequence[_T_co]: ...
    def __len__(self, /) -> int: ...


Device = _device

Dtype = _DType

Info = __array_namespace_info__

if sys.version_info >= (3, 12):
    from collections.abc import Buffer as SupportsBufferProtocol
else:
    SupportsBufferProtocol = Any

PyCapsule = Any

class SupportsDLPack(Protocol):
    def __dlpack__(self, /, *, stream: None = ...) -> PyCapsule: ...

Capabilities = TypedDict(
    "Capabilities", {"boolean indexing": bool, "data-dependent shapes": bool,
                     "max dimensions": int}
)

DefaultDataTypes = TypedDict(
    "DefaultDataTypes",
    {
        "real floating": Dtype,
        "complex floating": Dtype,
        "integral": Dtype,
        "indexing": Dtype,
    },
)

DataTypes = TypedDict(
    "DataTypes",
    {
        "bool": Dtype,
        "float32": Dtype,
        "float64": Dtype,
        "complex64": Dtype,
        "complex128": Dtype,
        "int8": Dtype,
        "int16": Dtype,
        "int32": Dtype,
        "int64": Dtype,
        "uint8": Dtype,
        "uint16": Dtype,
        "uint32": Dtype,
        "uint64": Dtype,
    },
    total=False,
)
