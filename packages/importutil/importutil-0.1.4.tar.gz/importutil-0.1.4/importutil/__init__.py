import importlib.util
import site
import sys
from pathlib import Path
from types import ModuleType

from .version import __version__  # noqa: F401


def is_venv() -> bool:
    """
    Check if Python is running inside a virtual environment.

    Returns:
        bool: True if running inside a virtual environment, False otherwise.
    """
    return sys.prefix != sys.base_prefix


def is_package_installed(name: str, package: str = None) -> bool:
    """
    Check if a Python package or module is installed.

    Args:
        name (str): The name of the module or package to check.
        package (str, optional): The package context to resolve relative imports (usually None).

    Returns:
        bool: True if the package is installed, False otherwise.
    """
    return importlib.util.find_spec(name, package=package) is not None


def get_sys_path() -> list[str]:
    """
    Return a copy of the current Python import search paths (sys.path).

    Returns:
        list[str]: A copy of the sys.path list.
    """
    return sys.path.copy()


def add_sys_path(path: str, index: int = 0) -> str:
    """
    Add a path to sys.path if not already present.

    Args:
        path (str): The path to add.
        index (int, optional): Position in sys.path to insert the path. Default is 0 (the beginning).

    Returns:
        str: The normalized absolute path that was added or already present.
    """
    path = str(Path(path).resolve())
    if path not in sys.path:
        sys.path.insert(index, path)
    return path


def import_file(file: str) -> ModuleType:
    """
    Dynamically import a Python file as a module.

    Args:
        file (str): Path to the .py file.

    Returns:
        ModuleType: The imported module.
    """
    file = Path(file).resolve()
    if not file.is_file():
        raise FileNotFoundError(f"File not found: {file}")

    name = file.stem
    spec = importlib.util.spec_from_file_location(name, str(file))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


def import_file2(file: str, package: str = None) -> ModuleType:
    """
    Dynamically import a Python file as a module.

    Args:
        file (str): Path to the .py file.

    Returns:
        ModuleType: The imported module.
    """
    file = Path(file).resolve()
    if not file.is_file():
        raise FileNotFoundError(f"File not found: {file}")

    path = str(file.parent)

    original_sys_path = None

    if path not in sys.path:
        original_sys_path = get_sys_path()
        add_sys_path(path)  # append to front

    module = importlib.import_module(name=file.stem, package=package)

    # restore sys path
    if original_sys_path is not None:
        sys.path = original_sys_path

    return module


def import_module(name: str, package: str = None) -> ModuleType:
    """
    Import or reload a module by name.

    Args:
        module_name (str): Name of the module to import.

    Returns:
        ModuleType: The imported module.
    """
    return importlib.import_module(name=name, package=package)


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
