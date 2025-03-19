"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.util.env import Env
from iprm.util.dir import CurrentSourceDir, SourceDir, RootRelativeSourceDir
from iprm.api.obj.project import Project
from iprm.api.obj.subdirectories import SubDirectories
from iprm.api.obj.cxx import CppExecutable, CppStaticLibrary, CppSharedLibrary, CppTest, CppThirdParty, BoostThirdParty, \
    QtThirdParty, PyBind11ThirdParty, IcuThirdParty
from iprm.api.obj.rust import RustExecutable

NAMESPACE = {
    # Utilities
    Env.__name__: Env,
    CurrentSourceDir.__name__: CurrentSourceDir,
    SourceDir.__name__: SourceDir,
    RootRelativeSourceDir.__name__: RootRelativeSourceDir,

    # Objects
    Project.__name__: Project,
    SubDirectories.__name__: SubDirectories,

    # C++ Targets
    CppExecutable.__name__: CppExecutable,
    CppStaticLibrary.__name__: CppStaticLibrary,
    CppSharedLibrary.__name__: CppSharedLibrary,
    CppTest.__name__: CppTest,

    CppThirdParty.__name__: CppThirdParty,
    BoostThirdParty.__name__: BoostThirdParty,
    QtThirdParty.__name__: QtThirdParty,
    PyBind11ThirdParty.__name__: PyBind11ThirdParty,
    IcuThirdParty.__name__: IcuThirdParty,

    # Rust Targets
    RustExecutable.__name__: RustExecutable,
}
