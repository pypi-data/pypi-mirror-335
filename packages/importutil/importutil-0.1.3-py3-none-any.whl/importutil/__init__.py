import importlib.util
import site
import sys
from pathlib import Path
from types import ModuleType

from version import __version__  # noqa: F401


def is_venv() -> bool:
    """
    Check if Python is running inside a virtual environment.

    Returns:
        bool: True if running inside a virtual environment, False otherwise.
    """
    return sys.prefix != sys.base_prefix


def is_package_installed(package_name: str) -> bool:
    """
    Check if a Python package is installed.

    Args:
        package_name (str): The name of the package to check.

    Returns:
        bool: True if the package is installed, False otherwise.
    """
    return importlib.util.find_spec(package_name) is not None


def get_sys_path() -> list[str]:
    """
    Return a copy of the current Python import search paths (sys.path).

    Returns:
        list[str]: A copy of the sys.path list.
    """
    return sys.path.copy()


def add_sys_path(path: str | Path) -> Path:
    """
    Add a path to sys.path if not already present.

    Args:
        path (str | Path): The path to add.

    Returns:
        Path: The normalized absolute Path that was added or already present.
    """
    path = Path(path).resolve()
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    return path


def create_pth_file(path: str | list[str], only_venv: bool = True) -> None:
    """
    Create a .pth file in site-packages to auto-load paths.

    Args:
        path: Directory or list of directories.
        only_venv: Only run if in a virtual environment.
    """
    if only_venv and not is_venv():
        return

    site_packages = Path(site.getsitepackages()[0])
    pth_file = site_packages / "importutil.pth"

    if not isinstance(path, list):
        path = [path]
    path = [Path(p).resolve() for p in path]
    path = [p for p in path if p.is_dir()]

    with open(pth_file, "w") as f:
        for p in path:
            f.write(str(p) + "\n")


def import_file(file: str | Path) -> ModuleType:
    """
    Dynamically import a Python file as a module.

    Args:
        file (str | Path): Path to the .py file.

    Returns:
        ModuleType: The imported module.
    """
    file = Path(file).resolve()
    if not file.is_file():
        raise FileNotFoundError(f"File not found: {file}")

    path = str(file.parent)

    original_sys_path = None

    if path not in sys.path:
        original_sys_path = sys.path.copy()
        # append to front
        sys.path = [path, *sys.path]

    module = importlib.import_module(file.stem)

    # restore sys path
    if original_sys_path is not None:
        sys.path = original_sys_path

    return module


def import_module(module_name: str) -> ModuleType:
    """
    Import or reload a module by name.

    Args:
        module_name (str): Name of the module to import.

    Returns:
        ModuleType: The imported module.
    """
    return importlib.import_module(module_name)
