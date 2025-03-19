import os
import tempfile
from pathlib import Path


def find_vcvarsall():
    program_files_64 = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_32 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    editions = ["Enterprise", "Professional", "Community"]
    vs_paths = []
    vs2022_paths = [
        f"{program_files_64}/Microsoft Visual Studio/2022/{edition}/VC/Auxiliary/Build/vcvarsall.bat"
        for edition in editions
    ]
    vs_paths.extend(vs2022_paths)
    legacy_vs_paths = []
    for version in ["2019", "2017"]:
        for edition in editions:
            legacy_vs_paths.append(
                f"{program_files_32}/Microsoft Visual Studio/{version}/{edition}/VC/Auxiliary/Build/vcvarsall.bat"
            )
    vs_paths.extend(legacy_vs_paths)
    for path in vs_paths:
        if Path(path).exists():
            return path
    return None


def vcvarsall_script(command):
    vcvarsall_path = find_vcvarsall()
    assert vcvarsall_path is not None
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.bat', delete=False, mode='w') as vcvarsall_batch:
        temp_script_path = vcvarsall_batch.name
        vcvarsall_batch.write("@echo off\n")
        vcvarsall_batch.write(f'call "{vcvarsall_path}" x64\n')
        vcvarsall_batch.write(f'{command}\n')
        return temp_script_path
