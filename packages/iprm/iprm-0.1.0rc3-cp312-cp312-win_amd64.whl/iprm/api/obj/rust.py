"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.api.obj.target import Target
from iprm.core.typeflags import RUST, EXECUTABLE
from iprm.util.dir import Dir
from iprm.util.compiler import RUSTC_COMPILER_NAME


class RustTarget(Target):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from iprm.api.obj.project import Project
        self.type_flags |= (RUST | Project.rust_compiler_flag())
        self.hex_colour = '#E68900'
        self.properties['manifest']: tuple[Dir, str] = None
        self.properties['cargo_locked']: bool = None
        self.properties['sources']: dict[Dir, list[str]] = {}

    # TODO: Support direct/manual rust complication (via the actual rust compiler) instead of forcing cargo/crate infra
    def crate(self, manifest_dir: Dir, cargo_file: str, locked: bool = False):
        self.shape_type = 'ellipse'
        self.properties['manifest'] = (manifest_dir, cargo_file)
        self.properties['cargo_locked'] = locked

    def sources(self, src_dir: Dir, *sources):
        if src_dir not in self.properties['sources']:
            self.properties['sources'][src_dir] = []
        self.properties['sources'][src_dir].extend(sources)

    @classmethod
    def default_compiler_name(cls):
        return RUSTC_COMPILER_NAME

    @classmethod
    def default_language_properties(cls, **kwargs):
        defaults = {}
        for key, value in defaults.items():
            kwargs.setdefault(key, value)
        return kwargs


class RustExecutable(RustTarget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diamond()
        self.type_flags |= EXECUTABLE
