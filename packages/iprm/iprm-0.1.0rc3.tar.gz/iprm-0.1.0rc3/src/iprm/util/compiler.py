import os
import sys
import tempfile
import subprocess
from typing import Optional, Callable
from iprm.core.typeflags import MSVC, CLANG, GCC, RUSTC
from iprm.util.env import Env

COMPILER_NAME_KEY = 'compiler'

STANDARD_VERSION_ARG = '--version'

# CXX
MSVC_COMPILER_NAME = 'msvc'
MSVC_CLANG_COMPILER_NAME = 'msvc-clang'
CLANG_COMPILER_NAME = 'clang'
GCC_COMPILER_NAME = 'gcc'

CXX_COMPILER_FLAGS = {
    MSVC_COMPILER_NAME: MSVC,
    MSVC_CLANG_COMPILER_NAME: CLANG,
    CLANG_COMPILER_NAME: CLANG,
    GCC_COMPILER_NAME: GCC,
}

CXX_COMPILER_BINARIES = {
    MSVC_COMPILER_NAME: 'cl',
    MSVC_CLANG_COMPILER_NAME: 'clang-cl',
    CLANG_COMPILER_NAME: 'clang++',
    GCC_COMPILER_NAME: 'g++',
}

CXX_COMPILER_VERSION_ARGUMENTS = {
    MSVC_COMPILER_NAME: '2>&1',
    MSVC_CLANG_COMPILER_NAME: STANDARD_VERSION_ARG,
    CLANG_COMPILER_NAME: STANDARD_VERSION_ARG,
    GCC_COMPILER_NAME: STANDARD_VERSION_ARG,
}

# RUST
RUSTC_COMPILER_NAME = 'rustc'

RUST_COMPILER_FLAGS = {
    RUSTC_COMPILER_NAME: RUSTC,
}

RUST_COMPILER_BINARIES = {
    RUSTC_COMPILER_NAME: 'rustc'
}

RUST_COMPILER_VERSION_ARGUMENTS = {
    RUSTC_COMPILER_NAME: STANDARD_VERSION_ARG,
}


def _parse_standard_version_output(output: str) -> str:
    lines = []
    for line in output.split("\n"):
        if line.strip() and not line.startswith("###"):
            lines.append(line)
        elif line.startswith("###"):
            break
    return "\n".join(lines).strip()


def _parse_gcc_version_output(output: str) -> str:
    return _parse_standard_version_output(output)


def _parse_clang_version_output(output: str) -> str:
    lines = output.strip().split("\n")
    for i, line in enumerate(lines):
        if "clang version" in line:
            return "\n".join(lines[i:i + 4]).strip()
    return output.strip()


def _parse_cl_version_output(output: str) -> str:
    output_lines = output.strip().split("\n")
    return "\n".join(output_lines[:2]).strip()


CXX_COMPILER_VERSION_PARSERS = {
    MSVC_COMPILER_NAME: _parse_cl_version_output,
    MSVC_CLANG_COMPILER_NAME: _parse_clang_version_output,
    CLANG_COMPILER_NAME: _parse_clang_version_output,
    GCC_COMPILER_NAME: _parse_gcc_version_output,
}

RUST_COMPILER_VERSION_PARSERS = {
    RUSTC_COMPILER_NAME: _parse_standard_version_output,
}


def _compiler_version_windows(binary_name: str, version_args: str, parser: Callable,
                              requires_vcvarsall: bool = False) -> Optional[str]:
    batch_script = ["@echo off"]

    if requires_vcvarsall:
        from iprm.util.vcvarsall import find_vcvarsall
        vcvarsall_path = find_vcvarsall()

        if vcvarsall_path is None:
            return None

        batch_script.extend([
            f'call "{vcvarsall_path}" x64'
        ])

    version_command = f'{binary_name} {version_args}'
    batch_script.extend([
        f'echo ###BEGIN_VERSION_CHECK###',
        f'where {binary_name} >nul 2>&1',
        'if %ERRORLEVEL% EQU 0 (',
        f'  echo ###COMPILER_AVAILABLE###',
        f'  {version_command}',
        ') else (',
        f'  echo ###COMPILER_NOT_AVAILABLE###',
        ')',
        f'echo ###END_VERSION_CHECK###'
    ])

    with tempfile.NamedTemporaryFile(suffix='.bat', delete=False, mode='w') as script_file:
        script_path = script_file.name
        for line in batch_script:
            script_file.write(f"{line}\n")

    try:
        # Use CREATE_NO_WINDOW flag on Windows to prevent command window from showing
        startupinfo = None
        if Env.platform.windows:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE

        result = subprocess.run(script_path,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                errors='replace',
                                startupinfo=startupinfo)

        output = result.stdout + result.stderr

        start_marker = "###BEGIN_VERSION_CHECK###"
        end_marker = "###END_VERSION_CHECK###"
        available_marker = "###COMPILER_AVAILABLE###"

        if start_marker in output and end_marker in output:
            check_section = output.split(start_marker)[1].split(end_marker)[0].strip()

            if available_marker in check_section:
                version_output = check_section.split(available_marker)[1].strip()
                version_str = parser(version_output)
                return version_str

        return None
    except Exception as e:
        print(f"Error checking Windows compiler: {str(e)}", file=sys.stderr)
        return None
    finally:
        try:
            os.unlink(script_path)
        except:
            pass


def _compiler_version_unix(binary_name: str, version_args: str, parser: Callable) -> Optional[str]:
    shell_script = [
        "#!/bin/bash",
        'echo "###BEGIN_VERSION_CHECK###"',
        f'if command -v {binary_name} >/dev/null 2>&1; then',
        f'  echo "###COMPILER_AVAILABLE###"',
        f'  {binary_name} {version_args}',
        'else',
        f'  echo "###COMPILER_NOT_AVAILABLE###"',
        'fi',
        'echo "###END_VERSION_CHECK###"'
    ]

    with tempfile.NamedTemporaryFile(suffix='.sh', delete=False, mode='w') as script_file:
        script_path = script_file.name
        for line in shell_script:
            script_file.write(f"{line}\n")

    os.chmod(script_path, 0o755)

    try:
        result = subprocess.run(script_path,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                errors='replace')

        output = result.stdout + result.stderr

        start_marker = "###BEGIN_VERSION_CHECK###"
        end_marker = "###END_VERSION_CHECK###"
        available_marker = "###COMPILER_AVAILABLE###"

        if start_marker in output and end_marker in output:
            check_section = output.split(start_marker)[1].split(end_marker)[0].strip()

            if available_marker in check_section:
                version_output = check_section.split(available_marker)[1].strip()
                version_str = parser(version_output)
                return version_str

        return None
    except Exception as e:
        print(f"Error checking Unix compiler: {str(e)}", file=sys.stderr)
        return None
    finally:
        try:
            os.unlink(script_path)
        except:
            pass


def cxx_compiler_version(compiler_name: str) -> Optional[str]:
    if compiler_name not in CXX_COMPILER_BINARIES:
        return None

    binary_name = CXX_COMPILER_BINARIES[compiler_name]
    version_args = CXX_COMPILER_VERSION_ARGUMENTS[compiler_name]
    parser = CXX_COMPILER_VERSION_PARSERS[compiler_name]
    requires_vcvarsall = compiler_name in [MSVC_COMPILER_NAME, MSVC_CLANG_COMPILER_NAME]

    if Env.platform.windows:
        return _compiler_version_windows(binary_name, version_args, parser, requires_vcvarsall)
    else:
        return _compiler_version_unix(binary_name, version_args, parser)


def rust_compiler_version(compiler_name: str) -> Optional[str]:
    if compiler_name not in RUST_COMPILER_BINARIES:
        return None

    binary_name = RUST_COMPILER_BINARIES[compiler_name]
    version_args = RUST_COMPILER_VERSION_ARGUMENTS[compiler_name]
    parser = RUST_COMPILER_VERSION_PARSERS[compiler_name]

    if Env.platform.windows:
        return _compiler_version_windows(binary_name, version_args, parser)
    else:
        return _compiler_version_unix(binary_name, version_args, parser)
