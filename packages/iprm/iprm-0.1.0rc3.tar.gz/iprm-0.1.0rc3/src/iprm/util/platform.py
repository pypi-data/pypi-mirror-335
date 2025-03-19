import platform
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

WINDOWS_PLAT_NAME = 'Windows'
MACOS_PLAT_NAME = 'Darwin'
LINUX_PLAT_NAME = 'Linux'


@dataclass
class PlatformContext:
    windows = False
    macos = False
    linux = False

    @property
    def platform_name(self) -> str:
        if self.windows:
            return WINDOWS_PLAT_NAME
        elif self.macos:
            return MACOS_PLAT_NAME
        elif self.linux:
            return LINUX_PLAT_NAME
        raise


@dataclass
class WindowsPlatformContext(PlatformContext):
    windows = True


@dataclass
class MacOSPlatformContext(PlatformContext):
    macos = True


@dataclass
class LinuxPlatformContext(PlatformContext):
    linux = True


PLATFORMS = [WINDOWS_PLAT_NAME, MACOS_PLAT_NAME, LINUX_PLAT_NAME]

PLAT_DISPLAY_NAME = {
    WINDOWS_PLAT_NAME: WINDOWS_PLAT_NAME,
    MACOS_PLAT_NAME: 'macOS',
    LINUX_PLAT_NAME: LINUX_PLAT_NAME,
}

PLAT_CONTEXT_TYPE = {
    WINDOWS_PLAT_NAME: WindowsPlatformContext,
    MACOS_PLAT_NAME: MacOSPlatformContext,
    LINUX_PLAT_NAME: LinuxPlatformContext,
}

_current_platform_context: Optional[PlatformContext] = None


def is_platform_ctx_set():
    return _current_platform_context is not None


def active_platform_name():
    return _current_platform_context.platform_name if _current_platform_context else platform.system()


@contextmanager
def platform_context(platform_context: PlatformContext):
    global _current_platform_context
    previous_context = _current_platform_context
    _current_platform_context = platform_context
    try:
        yield
    finally:
        _current_platform_context = previous_context


class Platform:
    def __init__(self):
        global _current_platform_context
        if _current_platform_context is not None:
            self.windows = _current_platform_context.windows
            self.macos = _current_platform_context.macos
            self.linux = _current_platform_context.linux
        else:
            os_name = platform.system()
            self.windows = os_name == WINDOWS_PLAT_NAME
            self.macos = os_name == MACOS_PLAT_NAME
            self.linux = os_name == LINUX_PLAT_NAME

        assert sum([self.windows, self.macos, self.linux]) == 1, "Only one platform can be active at a time"

    @staticmethod
    def display_name():
        return PLAT_DISPLAY_NAME[active_platform_name()]
