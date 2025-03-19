"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.core.object import Object
from iprm.core.typeflags import PROJECT, TypeFlags
from iprm.util.env import Env
from iprm.util.compiler import COMPILER_NAME_KEY, CXX_COMPILER_FLAGS, CXX_COMPILER_BINARIES, RUST_COMPILER_FLAGS, \
    RUST_COMPILER_BINARIES
from iprm.api.obj.cxx import CppTarget
from iprm.api.obj.rust import RustTarget


class Project(Object):
    _cxx_compiler_name: str = CppTarget.default_compiler_name()
    _cxx_compiler_flag: TypeFlags = CXX_COMPILER_FLAGS[CppTarget.default_compiler_name()]
    _cxx_compiler_bin: str = CXX_COMPILER_BINARIES[CppTarget.default_compiler_name()]
    _rust_compiler_name: str = RustTarget.default_compiler_name()
    _rust_compiler_flag: TypeFlags = RUST_COMPILER_FLAGS[RustTarget.default_compiler_name()]
    _rust_compiler_bin: str = RUST_COMPILER_BINARIES[RustTarget.default_compiler_name()]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_flags = PROJECT
        self.hex_colour = '#FFC107'
        self.shape_type = 'star'
        self._root_dir = Env.meta.build_file.parent
        self._cxx_enabled = False
        self._rust_enabled = False

    @property
    def root_dir(self):
        return self._root_dir

    def version(self, version):
        self.properties['version'] = version

    def description(self, description):
        self.properties['description'] = description

    def url(self, url):
        self.properties['url'] = url

    def cxx(self, **kwargs):
        kwargs = CppTarget.default_language_properties(**kwargs)
        self._cxx_compiler_name = kwargs.get(COMPILER_NAME_KEY, CppTarget.default_compiler_name())
        self._cxx_compiler_flag = CXX_COMPILER_FLAGS[self._cxx_compiler_name]
        self._cxx_compiler_bin = CXX_COMPILER_BINARIES[self._cxx_compiler_name]
        self._enable_language(CppTarget.__name__, **kwargs)
        self._cxx_enabled = True

    @property
    def cxx_enabled(self):
        return self._cxx_enabled

    @classmethod
    def cxx_compiler_flag(cls) -> TypeFlags:
        return cls._cxx_compiler_flag

    @classmethod
    def cxx_compiler_binary(cls):
        return cls._cxx_compiler_bin

    @classmethod
    def cxx_compiler_version(cls):
        from iprm.util.compiler import cxx_compiler_version
        return cxx_compiler_version(cls._cxx_compiler_name)

    def rust(self, **kwargs):
        kwargs = RustTarget.default_language_properties(**kwargs)
        self._rust_compiler_name = kwargs.get(COMPILER_NAME_KEY, RustTarget.default_compiler_name())
        self._rust_compiler_flag = RUST_COMPILER_FLAGS[self._rust_compiler_name]
        self._rust_compiler_bin = RUST_COMPILER_BINARIES[self._rust_compiler_name]
        self._enable_language(RustTarget.__name__, **kwargs)
        self._rust_enabled = True

    @property
    def rust_enabled(self):
        return self._rust_enabled

    @classmethod
    def rust_compiler_flag(cls) -> TypeFlags:
        return cls._rust_compiler_flag

    @classmethod
    def rust_compiler_binary(cls):
        return cls._rust_compiler_bin

    @classmethod
    def rust_compiler_version(cls):
        from iprm.util.compiler import rust_compiler_version
        return rust_compiler_version(cls._rust_compiler_name)

    def _enable_language(self, language: str, **kwargs):
        if 'languages' not in self.properties:
            self.properties['languages'] = {}
        self.properties['languages'][language] = kwargs
