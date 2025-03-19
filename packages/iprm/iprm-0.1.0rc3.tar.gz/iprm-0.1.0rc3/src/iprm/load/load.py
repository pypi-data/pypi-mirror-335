"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from abc import ABC, abstractmethod
from iprm.util.sink import ConsoleLogSink
from iprm.util.platform import PLAT_CONTEXT_TYPE
from iprm.util.meta import Meta
from iprm.core.object import Object


class Loader(ABC):
    def __init__(self, project_dir: str, platform: str):
        super().__init__()
        self._project_dir = project_dir
        self._platform = platform
        self._platform_ctx = PLAT_CONTEXT_TYPE[platform]
        self._log_sink = ConsoleLogSink()
        self._backend = Meta().backend

    @property
    def backend(self):
        return self._backend

    @backend.setter
    def backend(self, backend):
        self._backend = backend

    @abstractmethod
    def load_project(self) -> dict[str, list[Object]]:
        pass

    @abstractmethod
    def load_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def file_name(self) -> str:
        pass

    @property
    def project_dir(self):
        return self._project_dir

    @property
    def platform(self):
        return self._platform

    @property
    def log_sink(self):
        return self._log_sink
