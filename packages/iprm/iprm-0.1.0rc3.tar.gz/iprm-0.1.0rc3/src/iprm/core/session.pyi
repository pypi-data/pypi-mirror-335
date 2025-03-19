"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from pathlib import Path
from typing import Optional
from iprm.core.typeflags import TypeFlags
from iprm.core.object import Object

FILE_NAME: str = ...


class Session:
    @classmethod
    def create(cls, root_dir: Path) -> None: ...

    @classmethod
    def destroy(cls) -> None: ...

    @classmethod
    def instance(cls) -> 'Session': ...

    @classmethod
    def get_object(cls, obj_name: str) -> Optional[Object]: ...

    @classmethod
    def get_objects(cls) -> dict[str, list[Object]]: ...

    @classmethod
    def is_object_type(cls, obj_name: str, type_flag: TypeFlags) -> bool: ...

    @classmethod
    def register_object(cls, obj: Object) -> None: ...

    @classmethod
    def begin_file_context(cls, file_path: str) -> None: ...

    @classmethod
    def end_file_context(cls) -> None: ...

    @classmethod
    def retrieve_loadable_files(cls) -> list[str]: ...

    @classmethod
    def root_relative_source_dir(cls) -> str: ...
