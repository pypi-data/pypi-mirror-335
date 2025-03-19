"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
import os
from pathlib import Path
from iprm.util.platform import platform_context, Platform
from iprm.util.meta import meta_context, Meta
from iprm.util.env import Env
from iprm.load.load import Loader
from iprm.api.namespace import NAMESPACE
from iprm.core.session import Session
from contextlib import contextmanager


@contextmanager
def loadable_file_context(loadable_file_path: str):
    Session.begin_file_context(loadable_file_path)
    try:
        yield
    finally:
        Session.end_file_context()


class PythonLoader(Loader):
    def __init__(self, project_dir: str, platform: str):
        super().__init__(project_dir, platform)

    def load_project(self) -> list[str]:
        pass

    def file_name(self) -> str:
        pass

    def load_file(self, file_path):
        with loadable_file_context(file_path):
            file_name = os.path.basename(file_path)
            with open(file_path, 'r') as f:
                file_contents = f.read()
                try:
                    with meta_context(self.backend, Path(file_path)):
                        Env.meta = Meta(loading=True)
                        code = compile(file_contents, file_name, 'exec')
                        self._load_code(code, NAMESPACE)
                except Exception as e:
                    self._log_sink.log_exception(e)

    def _load_code(self, code, namespace):
        with platform_context(self._platform_ctx):
            Env.plat = Platform()
            try:
                exec(code, globals(), namespace)
            except Exception as e:
                self._log_exception(e)

    def _log_exception(self, e):
        import traceback
        tb_str = traceback.format_exc()
        exception_type = type(e).__name__
        error_message = str(e)
        # Access additional attributes that some exceptions might have
        extra_attrs = {attr: getattr(e, attr) for attr in dir(e)
                       if not attr.startswith('__') and not callable(getattr(e, attr))}

        self._log_sink.log_exception(e=e, type=exception_type, message=error_message, traceback=tb_str,
                                     attrs=extra_attrs)
