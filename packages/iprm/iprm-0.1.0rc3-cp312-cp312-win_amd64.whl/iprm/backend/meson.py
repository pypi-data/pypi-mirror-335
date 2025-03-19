"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from itertools import zip_longest
from pathlib import Path
from iprm.util.env import Env
from iprm.util.dir import CurrentSourceDir
from iprm.backend.backend import ProjectModel
from iprm.load.native import NativeLoader
from iprm.api.obj.project import Project
from iprm.api.obj.subdirectories import SubDirectories
from iprm.api.obj.subdirectories import SubDirectories
from iprm.api.obj.target import Target
from iprm.api.obj.cxx import CppTarget
from iprm.api.obj.rust import RustTarget


class Meson(ProjectModel):
    _native_file_path: Path = None

    def __init__(self, native_loader: NativeLoader, **kwargs):
        kwargs['build_dir'] = 'builddir'
        native_loader.backend = self.name()
        super().__init__(native_loader, **kwargs)

    @classmethod
    def name(cls):
        return 'meson'

    @classmethod
    def generator_ninja(cls):
        return 'ninja'

    @classmethod
    def generator_xcode(cls):
        return 'xcode'

    @classmethod
    def generator_visual_studio(cls):
        return 'vs2022'

    @classmethod
    def generator_unix_makefile(cls):
        raise NotImplementedError('Meson does not natively support using Make as a backend')

    @property
    def generated_file_name(self):
        return 'meson.build'

    @property
    def release_build_type(self):
        return 'release'

    @classmethod
    def _generate_project(cls, project: Project):
        # https://github.com/mesonbuild/meson/issues/1752#issuecomment-1216718818
        # Unfortunately, Meson has quite a cumbersome way to specify the compiler,
        # it essentially forces you to use CMakes toolchain file concept, as it has no
        # inline build script method to set your compiler. It would be really nice if
        # it was done in the default_options section of the project() function.
        # Maybe one day!
        cls._native_file_path = project.root_dir / f'{project.name}-meson-native.txt'
        native_file_content = [
            '[binaries]',
        ]
        if project.cxx_enabled:
            native_file_content.append(f"cpp = '{project.cxx_compiler_binary()}'")
        if project.rust_enabled:
            native_file_content.append(f"rust = '{project.rust_compiler_binary()}'")
        native_file_content.append('')
        with open(cls._native_file_path, 'w') as file:
            file.write('\n'.join(native_file_content))

        meson_content = [
            f"project('{project.name}', ",
        ]
        langs_dict = project.properties.get('languages', {})
        meson_content_def_options = ["\tdefault_options : [\n"]
        cxx_std_conformance = False
        if langs_dict:
            meson_content[-1] += '['
            langs_list = list(langs_dict.items())
            for (lang_type, lang_props), next_lang in zip_longest(langs_list, langs_list[1:], fillvalue=None):
                if lang_type == CppTarget.__name__:
                    standard = lang_props.get(CppTarget.STANDARD, None)
                    if standard:
                        meson_content_def_options[-1] += f"\t\t'cpp_std=c++{standard}',\n"
                    cxx_std_conformance = lang_props.get('conformance')
                    meson_content[-1] += "'cpp', "
                elif lang_type == RustTarget.__name__:
                    meson_content[-1] += "'rust', "
            meson_content[-1] += '],'

        meson_content_def_options[-1] += '\t]'

        meson_content.append(f"\tversion : '{project.properties.get('version', '0.1.0')}',")
        meson_content.extend(meson_content_def_options)
        meson_content.append(f')')
        meson_content.append('')

        # TODO: is this the best equivalent to what CMake can have? Or is there something better
        description = project.properties.get('description', None)
        if description:
            meson_content.append(f"summary('description', '{description}')")

        url = project.properties.get('url', None)
        if url:
            meson_content.append(f"summary('homepage_url', '{url}')")

        if Env.platform.windows and cxx_std_conformance:
            meson_content.append("if meson.get_compiler('cpp').get_id() == 'msvc'")
            meson_content.append("\tadd_project_arguments('/Zc:__cplusplus', '/permissive-', language : 'cpp')")
            meson_content.append('endif')
            meson_content.append('')

        # NOTE: From initial testing with Visual Studio, it looks like CMake automatically creates the projects
        #   relative to their folder hierarchy, where-as we have to explicitly do that in CMake, otherwise
        #   everything gets inline
        return meson_content

    @classmethod
    def _generate_subdirectories(cls, subdirs: SubDirectories):
        meson_content = []
        dir_paths = subdirs.properties.get('directory_paths', [])
        if dir_paths:
            for dir_path in dir_paths:
                meson_content.append(f"subdir('{dir_path}')")
        meson_content.append('')
        return meson_content

    @classmethod
    def _generate_target(cls, target: Target):
        pass

    @classmethod
    def _generate_cxx(cls, cxx: CppTarget):
        def add_sources(key):
            meson_content_sources = []
            sources_dict = cxx.properties.get(key, {})
            if sources_dict:
                for src_dir, src_files in sources_dict.items():
                    for src_file in src_files:
                        src_path = f"{cls.current_src_dir()} / '{src_file}'" \
                            if src_dir == CurrentSourceDir() else f"{cls.current_src_dir()} / '{src_dir.path.as_posix()}/{src_file}'"
                        meson_content_sources.append(f"\t{src_path},")
            return meson_content_sources

        target = cxx.name
        meson_content = []
        if cxx.is_app or cxx.is_test:
            meson_content.append(f"{target} = executable('{target}',")
        elif cxx.is_static:
            meson_content.append(f"static_library('{target}',")
        elif cxx.is_shared:
            meson_content.append(f"shared_library('{target}',")
        else:
            # If we didn't recognize/support the type, don't generate any content
            return meson_content
        meson_content.extend(add_sources('headers'))
        meson_content.extend(add_sources('sources'))
        meson_content.append(')')
        meson_content.append('')

        if cxx.is_test:
            meson_content.append(f"test('{target}',")
            meson_content.append(f"\t{target},")
            meson_content.append(')')
            meson_content.append('')

        # TODO: register test target properly, add our own _generate_<type> for all the third party and stuff that is
        #  needed

        return meson_content

    @classmethod
    def _generate_rust(cls, rust: RustTarget):
        target = rust.name
        manifest_dir, cargo_file = rust.properties.get('manifest')
        manifest_file = f"{cls.current_src_dir()} / '{cargo_file}'" \
            if manifest_dir == CurrentSourceDir() else f"{cls.current_src_dir()} / '{manifest_dir.path.as_posix()}/{cargo_file}'"

        meson_inputs_content = '\tinput: files(\n'
        meson_inputs_content += f'\t\t{manifest_file},\n'
        sources_dict = rust.properties.get('sources', {})
        if sources_dict:
            for src_dir, src_files in sources_dict.items():
                for src_file in src_files:
                    src_path = f"{cls.current_src_dir()} / '{src_file}'" \
                        if src_dir == CurrentSourceDir() else f"{cls.current_src_dir()} / '{src_dir.path.as_posix()}/{src_file}'"
                    meson_inputs_content += f"\t\t{src_path},\n"
        meson_inputs_content += '\t),'

        meson_content = [
            "cargo_profile = 'dev'",
            "if get_option('buildtype') == 'release' or get_option('buildtype') == 'minsize'",
            "\tcargo_profile = 'release'",
            "endif",
            "",
            f"custom_target('{target}',",
            meson_inputs_content,
            f"\toutput : '{target}',",
            "\tconsole : true,",
            "\tcommand : [",
            "\t\tfind_program('cargo'),",
            "\t\t'build',",
            f"\t\t'--manifest-path', {manifest_file},",
            "\t\t'--target-dir', meson.current_build_dir(),",
            "\t\t'--profile', cargo_profile,",
        ]
        cargo_locked = rust.properties.get('cargo_locked', False)
        if cargo_locked:
            meson_content.append("\t\t'--locked'")
        meson_content.append("\t],")
        meson_content.append("\tbuild_by_default : true,")
        meson_content.append(")")
        meson_content.append('')
        return meson_content

    @classmethod
    def current_src_dir(cls):
        return 'meson.current_source_dir()'

    @classmethod
    def current_bin_dir(cls):
        return 'meson.current_build_dir()'

    @classmethod
    def configure(cls, **kwargs):
        generator = kwargs.get('generator')
        srcdir = kwargs.get('srcdir')
        bindir = kwargs.get('bindir')
        cmd = [
            'meson',
            'setup',
            '--reconfigure',
            srcdir,
            bindir,
            f'--backend={generator}',
            f'--buildtype={cls.build_type(**kwargs)}',
        ]
        # TODO: Remove this as we want target-specific compilers
        native_file = cls._native_file_path
        if native_file:
            cmd.append(f'--native-file="{str(native_file)}')
        return cls._run_command(cmd)

    @classmethod
    def build(cls, **kwargs):
        bindir = kwargs.get('bindir')
        target = kwargs.get('target', None)
        cmd = [
            'meson',
            'compile',
            '-C',
            bindir,
            f'-j{cls.num_procs(**kwargs)}'
        ]
        if target:
            cmd.append(target)
        return cls._run_command(cmd)

    @classmethod
    def _default_build_type(cls):
        cls._release_build_type()

    @classmethod
    def _release_build_type(cls):
        return 'release'

    @classmethod
    def _debug_build_type(cls):
        return 'debug'

    @classmethod
    def test(cls, **kwargs):
        bindir = kwargs.get('bindir')
        cmd = [
            'meson',
            'test',
            '-C',
            bindir,
        ]
        return cls._run_command(cmd)

    @classmethod
    def install(cls, **kwargs):
        # TODO: impl install
        pass
