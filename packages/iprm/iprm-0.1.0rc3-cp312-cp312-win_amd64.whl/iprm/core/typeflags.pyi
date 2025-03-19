"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from enum import IntFlag
from typing import ClassVar


class TypeFlags(IntFlag):
    NONE: ClassVar[TypeFlags]
    PROJECT: ClassVar[TypeFlags]
    SUBDIRS: ClassVar[TypeFlags]
    TARGET: ClassVar[TypeFlags]
    TEST: ClassVar[TypeFlags]
    EXECUTABLE: ClassVar[TypeFlags]
    LIBRARY: ClassVar[TypeFlags]
    HEADER: ClassVar[TypeFlags]
    STATIC: ClassVar[TypeFlags]
    SHARED: ClassVar[TypeFlags]
    THIRDPARTY: ClassVar[TypeFlags]
    PKGCONFIG: ClassVar[TypeFlags]
    PRECOMPILEDARCHIVE: ClassVar[TypeFlags]
    SOURCEARCHIVE: ClassVar[TypeFlags]
    GIT: ClassVar[TypeFlags]
    VCPKG: ClassVar[TypeFlags]
    CONAN: ClassVar[TypeFlags]
    APT: ClassVar[TypeFlags]
    DNF: ClassVar[TypeFlags]
    CONTAINER: ClassVar[TypeFlags]
    CRTSTATIC: ClassVar[TypeFlags]
    CRTDYNAMIC: ClassVar[TypeFlags]
    CRTDUAL: ClassVar[TypeFlags]
    CXX: ClassVar[TypeFlags]
    RUST: ClassVar[TypeFlags]
    BOOST: ClassVar[TypeFlags]
    QT: ClassVar[TypeFlags]
    PYBIND11: ClassVar[TypeFlags]
    ICU: ClassVar[TypeFlags]
    MSVC: ClassVar[TypeFlags]
    CLANG: ClassVar[TypeFlags]
    GCC: ClassVar[TypeFlags]
    RUSTC: ClassVar[TypeFlags]

    def __or__(self, other: TypeFlags) -> TypeFlags: ...

    def __and__(self, other: TypeFlags) -> TypeFlags: ...

    def __invert__(self) -> TypeFlags: ...

    def __int__(self) -> int: ...


# Export all enum values at module level
NONE: TypeFlags
PROJECT: TypeFlags
SUBDIRS: TypeFlags
TARGET: TypeFlags
TEST: TypeFlags
EXECUTABLE: TypeFlags
LIBRARY: TypeFlags
HEADER: TypeFlags
STATIC: TypeFlags
SHARED: TypeFlags
THIRDPARTY: TypeFlags
PKGCONFIG: TypeFlags
PRECOMPILEDARCHIVE: TypeFlags
SOURCEARCHIVE: TypeFlags
GIT: TypeFlags
VCPKG: TypeFlags
CONAN: TypeFlags
APT: TypeFlags
DNF: TypeFlags
CONTAINER: TypeFlags
CRTSTATIC: TypeFlags
CRTDYNAMIC: TypeFlags
CRTDUAL: TypeFlags
CXX: TypeFlags
RUST: TypeFlags
BOOST: TypeFlags
QT: TypeFlags
PYBIND11: TypeFlags
ICU: TypeFlags
MSVC: TypeFlags
CLANG: TypeFlags
GCC: TypeFlags
RUSTC: TypeFlags
