"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.core.core import TypeFlags

enum_values = {name: getattr(TypeFlags, name) for name in dir(TypeFlags)
               if not name.startswith('_') and not callable(getattr(TypeFlags, name))}

globals().update(enum_values)
