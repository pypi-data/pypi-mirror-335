"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.core.object import Object
from iprm.core.typeflags import TARGET

class Target(Object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_flags = TARGET
        self.properties['dependencies']: list[str] = []

    def requires(self, *targets):
        self.properties['dependencies'].extend(targets)

    @property
    def dependencies(self):
        return self.properties['dependencies']
