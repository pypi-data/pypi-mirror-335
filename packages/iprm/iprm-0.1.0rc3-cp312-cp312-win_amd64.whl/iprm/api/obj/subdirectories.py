"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.core.object import Object
from iprm.core.typeflags import SUBDIRS


class SubDirectories(Object):
    def __init__(self, *directory_paths):
        import uuid
        super().__init__(name=str(uuid.uuid4()))
        self.type_flags = SUBDIRS
        self.hex_colour = '#607D8B'
        self.shape_type = 'circle'
        self.properties['directory_paths'] = directory_paths
