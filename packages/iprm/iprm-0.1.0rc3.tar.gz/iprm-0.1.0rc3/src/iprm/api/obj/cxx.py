"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.api.obj.target import Target
from iprm.core.typeflags import CXX, STATIC, SHARED, EXECUTABLE, TEST, THIRDPARTY, PKGCONFIG, PRECOMPILEDARCHIVE, \
    SOURCEARCHIVE, GIT, VCPKG, CONAN, APT, DNF, BOOST, QT, PYBIND11, ICU
from iprm.util.dir import Dir
from iprm.util.env import Env
from iprm.util.compiler import MSVC_COMPILER_NAME, CLANG_COMPILER_NAME, GCC_COMPILER_NAME


class CppTarget(Target):
    STANDARD = 'standard'
    CONFORMANCE = 'conformance'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from iprm.api.obj.project import Project
        self.type_flags |= (CXX | Project.cxx_compiler_flag())
        self.hex_colour = '#3388CC'
        self.properties['headers']: dict[Dir, list[str]] = {}
        self.properties['sources']: dict[Dir, list[str]] = {}
        self.properties['defines']: list[str] = []

    @classmethod
    def default_compiler_name(cls):
        if Env.platform.windows:
            return MSVC_COMPILER_NAME
        elif Env.platform.macos:
            return CLANG_COMPILER_NAME
        elif Env.platform.linux:
            return GCC_COMPILER_NAME
        return None

    @classmethod
    def default_language_properties(cls, **kwargs):
        defaults = {
            cls.STANDARD: '20',
            cls.CONFORMANCE: True,
        }
        for key, value in defaults.items():
            kwargs.setdefault(key, value)
        return kwargs

    def headers(self, header_dir: Dir, *headers):
        if header_dir not in self.properties['headers']:
            self.properties['headers'][header_dir] = []
        self.properties['headers'][header_dir].extend(headers)

    def sources(self, src_dir: Dir, *sources):
        if src_dir not in self.properties['sources']:
            self.properties['sources'][src_dir] = []
        self.properties['sources'][src_dir].extend(sources)

    def defines(self, *defines):
        self.properties['defines'].extend(defines)


class CppExecutable(CppTarget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diamond()
        self.type_flags |= EXECUTABLE


class CppStaticLibrary(CppTarget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ellipse()
        self.type_flags |= STATIC


class CppSharedLibrary(CppTarget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ellipse()
        self.type_flags |= SHARED


class CppTest(CppTarget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circle()
        self.type_flags |= TEST


# TODO: If a backend doesn't have native support for any of these third party library types, then implement it via a
#  custom command
class CppThirdParty(CppTarget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_flags |= THIRDPARTY

    def source_archive(self):
        # TODO: (compile from source, can optionally send a list of patches to also apply)
        self.type_flags |= SOURCEARCHIVE

    def precompiled_archive(self):
        # TODO: platform specific binaries and (if a library) headers, add ability to pass in the archive file path
        #  (relative to project file) for all 3 platforms. only need to specify the ones you actually support, if I
        #  platform doesn't have a location, it will just get ignored at generate time
        self.type_flags |= PRECOMPILEDARCHIVE

    def git(self):
        # TODO: pull source from git, pass in a branch and a tag (e.g. FetchContent from CMake)
        self.type_flags |= GIT

    def vcpkg(self):
        # TODO: specify required vcpkg stuff here, ensure to only support the latest/modern way of doing things (I
        #  think that is some manifest stuff?)
        self.type_flags |= VCPKG

    def conan(self):
        # TODO: specify required conan stuff here
        self.type_flags |= CONAN

    def pkgconfig(self):
        # TODO: Some backend (e.g. CMake) have native support for this, so this impl will be relatively clean
        # NOTE: Use the freedesktop.svg logo for this int he target properties view
        self.type_flags |= PKGCONFIG

    # TODO: For the Linux distro-specific package managers below, as we will be manually linking their libraries, consumers need
    #  to specify the package name, the library name name we need to pass to the linker, and then the include path too

    # TODO: Also, the PRE_BUILD invocations to install the library will first call
    #  the relevant package manager command to determine if the user has already
    #  installed it or not. Or maybe for the first round just always attempt to
    #  install, given it only gets invoked if you need to re-build the target, so we should use a sentinel/timestamp
    #  file and store that in the binary dir the first time we invoke it

    def apt(self):
        # TODO: Debian-Based Advanced Package Tool, only will be acknowledged on Linux. But this will translate to a
        #  PRE_BUILD command (for CMake at least) and run apt-get on the list of packages you supply, and then directly
        #  linking with the library instead of trying to use something like find_package which requires things at
        #  configure time which is inefficient, we want things at build time so they can be parallelized.
        # NOTE: Use the debian.svg logo for this in the target properties view
        self.type_flags |= APT

    def dnf(self):
        # TODO: Fedora/RHEL/CentOS-Based Dandified YUM, also only acknowledged on Linux and same concept as above
        # NOTE: Use the fedora.svg logo for this in the target properties view
        self.type_flags |= DNF


class BoostThirdParty(CppThirdParty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_flags |= BOOST


# TODO: ensure example works with a precompiled qt-based archive, for cmake, archive is reqired to
#  contain the lib/cmake/Qt6 folder so we can jsut directly use find_package() inst this scenario and
#  all of qts machine CMake modules. This is why the explicitly tag we're qt so we can branch off
#  during cmake generation
class QtThirdParty(CppThirdParty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_flags |= QT


# TODO: do the same/similar branch off and use of mature CMake modules for pybind11, add it to our TypeFlags
#  enum to allow for this
class PyBind11ThirdParty(CppThirdParty):
    def __init__(self, py_major, py_minor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_flags |= PYBIND11
        # TODO: Pybind11 Targets should always implicitly depend on/link with python.
        self.properties['python_major_version'] = py_major
        self.properties['python_minor_version'] = py_minor


class IcuThirdParty(CppThirdParty):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_flags |= ICU
