import sys
from pathlib import Path


def default_seabird_exe_path() -> Path:
    """Creates a platform-dependent default path to the Sea-Bird exes."""
    exe_path = "Program Files (x86)/Sea-Bird/SBEDataProcessing-Win32/"
    if sys.platform.startswith("win"):
        path_prefix = Path("C:")
    else:
        path_prefix = Path.home().joinpath(".wine/drive_c")
    return path_prefix.joinpath(exe_path)
