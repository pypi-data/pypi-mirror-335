import platform
import sys
from typing import Optional


def _get_system_name() -> Optional[str]:
    platform_name = platform.system()
    if "Linux" == platform_name:
        return (
            f"{platform.system()}-{platform.machine()}-{platform.libc_ver()[0]}"
        )
    elif "Darwin" == platform_name:
        return f"{platform.system()}-{platform.machine()}"
    elif "Windows" == platform_name:
        return f"{platform.system()}-{platform.machine()}-{platform.win32_ver()[0]}"


def _get_os_name():
    platforms = {
        "linux1": "linux",
        "linux2": "linux",
        "darwin": "macos",
        "win32": "windows",
    }
    return (
        platforms[sys.platform] if sys.platform in platforms else sys.platform
    )


SYSTEM_NAME = _get_system_name()
OS_NAME = _get_os_name()
IS_PTY = sys.stdout.isatty() if OS_NAME != "windows" else False
IS_POSIX = OS_NAME != "win32"
