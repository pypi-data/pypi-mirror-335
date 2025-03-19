"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
from iprm.load.python import PythonLoader
from iprm.core.session import Session
from iprm.core.object import object_created_callback, Object
from iprm.api.obj.project import Project
from iprm import FILE_NAME


class NativeLoader(PythonLoader):
    def __init__(self, project_dir: str, platform: str):
        super().__init__(project_dir, platform)
        self._objects = {}
        self._project_object: Project = None

    # TODO: expose this rather than the general scenario, as we don't need that. We only deal with objects directly
    #  one file at a time. Let the Session handle all the management etc
    def objects_for_file(self, project_file_path):
        # TODO: This should just call Session.get_objects_for_file()
        pass

    def load_project(self):
        self._project_object = None
        loadable_project_entries = Session.retrieve_loadable_files()
        num_entries_to_load = len(loadable_project_entries)
        if num_entries_to_load == 0:
            self._log_sink.log_message(f'{self.file_name()}: no project files to load')
            return

        num_entries_loaded = 1
        for entry_file_path in loadable_project_entries:
            def load_log():
                self._log_sink.log_message(
                    f"[{num_entries_loaded}/{num_entries_to_load}] Loading '{entry_file_path}'", end='\r')

            load_log()

            objects_for_file = []

            def on_objects_created(obj: Object):
                from typing import cast
                if isinstance(obj, Project):
                    self._project_object = cast(Project, obj)
                objects_for_file.append(obj)

            with object_created_callback(on_objects_created):
                self.load_file(entry_file_path)

            self._objects[entry_file_path] = objects_for_file
            num_entries_loaded += 1
        self._log_sink.log_message('')
        return self._objects

    def load_files(self, loadable_project_entries: list[str]):
        for entry_file_path in loadable_project_entries:
            self.load_file(entry_file_path)

    def file_name(self) -> str:
        return FILE_NAME

    def display_compiler_version(self, **kwargs):
        self.load_project()
        self._log_sink.log_message(f'Identifying compiler...')
        if kwargs.get('cxx'):
            self._log_sink.log_message('')
            self._log_sink.log_message(self._project_object.cxx_compiler_version())
        elif kwargs.get('rust'):
            self._log_sink.log_message('')
            self._log_sink.log_message(self._project_object.rust_compiler_version())
