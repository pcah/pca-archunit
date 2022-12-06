import os
import pkgutil
import sys
import typing as t
from importlib import import_module
from pathlib import Path
from types import ModuleType

# TODO create own error classes
OwnImportError = ValueError
UnexpectedBehavior = RuntimeError


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


_INIT_FILE_NAME = "__init__"
_PYTHON_CODE_FILE_SUFFIXES = {".py", ".pyc"}
_IGNORED_DIRECTORY_NAMES = {"__pycache__"}


def iterate_modules(  # noqa: C901
    target: t.Union[str, ModuleType], recursive: bool = True, include_packages: bool = False
) -> t.Generator[ModuleType, None, None]:
    """
    Imports and iterates through all modules of a given module.

    * Supports PEP 420 (Implicit Namespace Packages), and so
    may iterate through test modules in codebase, even if hidden in `tests` of non-init directory structure.
    * May be recursive (by default) or not, depending on `recursive` flag.
    * May include intermediate packages iff `include_packages` flag is on.
    * NB: for now, the function doesn't consider packed packages like zipfiles and eggs.
    * NB: extended design comparing of just using `pkgutil.walk_packages`, because `walk_packages` ignores
    implicit packages.

    :param target: `builtins.module` object (which represents both single-file Python module and a Python package)
        or Python qualified name of such an object to import.
    :param recursive: looks into subpackages looking for modules (by default) or not.
    :param include_packages: yield also the intermediate packages while looking for modules or not (by default)

    Compare the following examples (order of the yields might be different, not all actual modules might be listed):

    >> iterate_modules("pca.packages.archunit", recursive=False)
    # pca.packages.archunit.cli
    # pca.packages.archunit.importing
    # pca.packages.archunit.introspection
    # pca.packages.archunit.register

    >> iterate_modules("pca.packages.archunit")
    # pca.packages.archunit.cli
    # pca.packages.archunit.importing
    # pca.packages.archunit.introspection
    # pca.packages.archunit.units.application   <--
    # pca.packages.archunit.units.base          <--
    # pca.packages.archunit.units.common        <--
    # pca.packages.archunit.register

    >> iterate_modules("pca.packages.archunit", recursive=False, include_packages=True)
    # pca.packages.archunit.cli
    # pca.packages.archunit.importing
    # pca.packages.archunit.introspection
    # pca.packages.archunit.units               <--
    # pca.packages.archunit.register

    >> iterate_modules("pca.packages.archunit", include_packages=True)
    # pca.packages.archunit.cli
    # pca.packages.archunit.importing
    # pca.packages.archunit.introspection
    # pca.packages.archunit.units               <--
    # pca.packages.archunit.units.application   <--
    # pca.packages.archunit.units.base          <--
    # pca.packages.archunit.units.common        <--
    # pca.packages.archunit.register
    """
    target = maybe_dotted_name(target)
    if not isinstance(target, ModuleType):
        raise OwnImportError(f"Target '{target}' is not a valid module or package: `{type(target)}` instead.")

    target_paths = _get_modules_target_paths(target)
    assert target_paths, f"`{target}` case is not covered by the function"

    for path in target_paths:
        if path.suffix in _PYTHON_CODE_FILE_SUFFIXES:
            # TODO is it possible for a py-file path to be other than from the case of py-file module?
            yield target
            continue
        checked = set()
        for module_info in pkgutil.walk_packages([str(path)]):
            checked.add(module_info.name)
            try:
                subtarget = import_module(f"{target.__name__}.{module_info.name}")
            except ImportError:  # pragma: no cover
                # TODO raise warning of non-importable package
                continue
            if module_info.ispkg:
                if include_packages:
                    yield subtarget
                if recursive:
                    # we need to go deeper :)
                    yield from iterate_modules(subtarget, recursive=recursive, include_packages=include_packages)
            else:
                yield subtarget

        if not recursive:
            continue
        # try with subtargets as PEP 420 – Implicit Namespace Packages
        for subpath in path.iterdir():
            if (
                subpath.stem in checked  # these has been identified as packages earlier
                or not subpath.is_dir()  # ignore non-dirs
                or subpath.name in _IGNORED_DIRECTORY_NAMES  # specifically ignore some directories like Python cache
            ):
                continue
            try:
                subtarget = import_module(f"{target.__name__}.{subpath.name}")
            except ImportError:
                continue
            if include_packages:
                yield subtarget
            # we need to go deeperer ;)
            yield from iterate_modules(subtarget, recursive=recursive, include_packages=include_packages)


def _get_modules_target_paths(target: ModuleType) -> t.Set[Path]:
    if target.__file__ is None:
        # case: PEP 420 – Implicit Namespace Packages
        # multiple directories to traverse
        # https://peps.python.org/pep-0420/
        assert hasattr(target, "__path__"), "Unexpected: no __file__ and no __path__: check PEP 420 for such case."
        # NB: Implicit packages' __path__ object - _NamespacePath class - has potential paths to codebase
        # under `._path` attribute
        return {Path(p) for p in getattr(target.__path__, "_path", ())}
    elif (path := Path(target.__file__)).suffix in _PYTHON_CODE_FILE_SUFFIXES:
        if path.stem == _INIT_FILE_NAME:
            # target is a standard case for a sourcefile-based package (__file__ points to an __init__.py)
            return {path.parent}
        # target is standard case for a py-file module
        return {path}

    raise UnexpectedBehavior("Unsupported case for Python module path.")  # pragma: no cover


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
