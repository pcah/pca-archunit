import inspect
import os
import pkgutil
import sys
import typing as t
from importlib import import_module
from pathlib import Path
from types import ModuleType

# TODO create own error classes
OwnImportError = ValueError


def maybe_dotted_name(sth: t.Any) -> t.Any:
    """
    Function that lets you give a dotted qualified name instead of an object.

    If it is an object, does nothing more than return it.
    If it is a string, assumes it is an dotted qualified name and tries to import it.
    """
    if isinstance(sth, str):
        return import_dotted_name(sth)
    return sth


# noinspection PyUnboundLocalVariable
def import_dotted_name(dotted_qualified_name: str) -> t.Any:
    """
    Import a dotted module path and return the attribute/class designated by
    the last name in the path. Raise ImportError if the import failed.

    Code taken from: django.utils.module_loading:import_string v 1.9

    NB: stdlib `pkgutil` has `resolve_name` function, which does approximately the same,
    but it is only available since Python 3.9.

    TODO (tombstone Python 3.8 end of life: 2024-10)
    """
    if ":" in dotted_qualified_name:
        module_path, attribute_path = dotted_qualified_name.rsplit(":", 1)
    else:
        module_path, attribute_path = dotted_qualified_name, None

    obj = import_module(module_path)

    if attribute_path is None:
        return obj

    try:
        for chunk in attribute_path.split("."):
            obj = getattr(obj, chunk)
    except AttributeError as e:
        raise ImportError(f"Module '{module_path}' does not define a '{attribute_path}' attribute/class") from e
    return obj


_INIT_FILE_NAME = "__init__.py"
_PYTHON_CODE_FILE_SUFFIXES = {".py", ".pyc"}


def iterate_modules(
    target: t.Union[str, ModuleType], recursive: bool = True, include_packages: bool = False
) -> t.Generator[ModuleType, None, None]:
    """
    WARNING: for now, the function doesn't consider packed packages like zipfiles and eggs.

    NB: alternative design than just using `pkgutil.walk_packages`, because `walk_packages` ignores
    implicit packages.
    """
    target = maybe_dotted_name(target)
    if not inspect.ismodule(target):
        raise OwnImportError(f"Target '{target}' is not a valid module or package: `{type(target)}` instead.")

    # we need to go deeper
    if target.__file__ is None:
        # case: PEP 420 – Implicit Namespace Packages
        # multiple directories to traverse
        # https://peps.python.org/pep-0420/
        assert hasattr(target, "__path__"), "Unexpected: no __file__ and no __path__: check PEP 420 for such case."
        target_paths = {Path(p) for p in target.__path__._path}
    elif (path := Path(target.__file__)).name == _INIT_FILE_NAME:
        # target is a standard case for a sourcefile-based package (__file__ points to an __init__.py)
        target_paths = {path.parent}
    elif path.suffix in _PYTHON_CODE_FILE_SUFFIXES:
        # target is a standard case for a py-file
        yield target
        return

    if include_packages:
        yield target

    for path in target_paths:
        for module_info in pkgutil.walk_packages([str(path)]):
            try:
                subtarget = import_module(f"{target.__name__}.{module_info.name}")
            except ImportError:
                continue
            if module_info.ispkg:
                if recursive:
                    # we need to go deeperer ;)
                    yield from iterate_modules(subtarget, recursive=recursive, include_packages=include_packages)
            else:
                yield subtarget

        if not recursive:
            continue
        # try with subtargets as PEP 420 – Implicit Namespace Packages
        for subpath in path.iterdir():
            if subpath.is_dir() and not (subpath / _INIT_FILE_NAME).exists():
                try:
                    subtarget = import_module(f"{target.__name__}.{subpath.name}")
                except ImportError:
                    continue
                # we need to go deepererer ;)
                yield from iterate_modules(subtarget, recursive=recursive, include_packages=include_packages)


def import_all_names(_file, _name):
    """
    Util for a tricky dynamic import of all names from all submodules.
    Use it in the __init__.py using following idiom:

        import_all_names(__file__, __name__)

    Supports __all__ attribute of the submodules.
    """
    path = os.path.dirname(os.path.abspath(_file))
    parent_module = sys.modules[_name]

    dir_list = []
    for py in [
        filename[:-3] for filename in os.listdir(path) if filename.endswith(".py") and filename != "__init__.py"
    ]:
        module = __import__(".".join([_name, py]), fromlist=[py])
        module_names = getattr(module, "__all__", None) or dir(module)
        objects = dict((name, getattr(module, name)) for name in module_names if not name.startswith("_"))
        for name, obj in objects.items():
            if hasattr(parent_module, name) and getattr(parent_module, name) is not obj:
                msg = (
                    "Function import_all_names hit upon conflicting " "names. '{0}' is already imported to {1} module."
                ).format(name, module)
                import warnings

                warnings.warn(msg)
            setattr(parent_module, name, obj)
        dir_list.extend(objects)
    parent_module.__dir__ = lambda: dir_list
