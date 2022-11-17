from importlib import import_module
from types import ModuleType
import inspect
import os
from pathlib import Path
import sys
import typing as t


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
    try:
        if ":" in dotted_qualified_name:
            module_path, qual_name = dotted_qualified_name.rsplit(":", 1)
        else:
            module_path, qual_name = dotted_qualified_name.rsplit(".", 1)
    except ValueError as e:
        msg = "'%s' doesn't look like a module path" % dotted_qualified_name
        raise ImportError(msg) from e

    obj = import_module(module_path)

    try:
        for chunk in qual_name.split("."):
            obj = getattr(obj, chunk)
    except AttributeError as e:
        msg = "Module '%s' does not define a '%s' attribute/class" % (module_path, qual_name)
        raise ImportError(msg) from e
    return obj


_INIT_FILE_NAME = "__init__.py"


def iterate_submodules(
    package: t.Union[str, ModuleType], recursive: bool = True
) -> t.Generator[ModuleType, None, None]:
    package = maybe_dotted_name(package)
    if package.__file__ is None:  # case: PEP 420 – Implicit Namespace Packages
        assert hasattr(package, "__path__"), "Unexpected: no __file__ and no __path__: check PEP 420 for such case."
        package_paths = {Path(p) for p in package.__path__._path}
    elif (path := Path(package.__file__)).name == _INIT_FILE_NAME:  # standard case for a package (__file__ points to an __init__.py)
        package_paths = {path.parent}
    elif path.suffix == ".py":  # standard case: a module
        package_paths = {Path(package.__file__)}
    # if package_path.endswith(_INIT_FILE_NAME):
    #     package_path = os.path.dirname(os.path.abspath(package_path))
    for path in package_paths:
        if path.is_file() and path.suffix == ".py":

    for py in [
        filename[:-3] for filename in os.listdir(path) if filename.endswith(".py") and filename != "__init__.py"
    ]:
        module = __import__(".".join([_name, py]), fromlist=[py])
        yield from inspect.getmembers(package, predicate=inspect.ismodule)


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
