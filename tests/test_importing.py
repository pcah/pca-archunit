import pytest

from pca.packages.archunit.importing import (
    OwnImportError,
    iterate_modules,
)


class TestIterateModules:
    def test_importing_implicit_package(self):
        assert list(m.__name__ for m in iterate_modules("importing_test_package")) == [
            "importing_test_package.implicit_package.spam",
            "importing_test_package.implicit_package.subpackage.bar.baz",
            "importing_test_package.implicit_package.subpackage.bar.quax",
            "importing_test_package.implicit_package.subpackage.bar.tests.standalone_test_module",
            "importing_test_package.implicit_package.subpackage.foo",
        ]

    def test_importing_implicit_package_including_packages(self):
        assert list(m.__name__ for m in iterate_modules("importing_test_package", include_packages=True)) == [
            "importing_test_package.implicit_package",
            "importing_test_package.implicit_package.spam",
            "importing_test_package.implicit_package.subpackage",
            "importing_test_package.implicit_package.subpackage.bar",
            "importing_test_package.implicit_package.subpackage.bar.baz",
            "importing_test_package.implicit_package.subpackage.bar.quax",
            "importing_test_package.implicit_package.subpackage.bar.tests",
            "importing_test_package.implicit_package.subpackage.bar.tests.standalone_test_module",
            "importing_test_package.implicit_package.subpackage.foo",
        ]

    def test_non_recursive_package(self):
        assert list(
            m.__name__ for m in iterate_modules("importing_test_package.implicit_package.subpackage", recursive=False)
        ) == ["importing_test_package.implicit_package.subpackage.foo"]
        assert list(
            m.__name__
            for m in iterate_modules("importing_test_package.implicit_package.subpackage.bar", recursive=False)
        ) == [
            "importing_test_package.implicit_package.subpackage.bar.baz",
            "importing_test_package.implicit_package.subpackage.bar.quax",
        ]

    def test_non_recursive_implicit_package(self):
        assert list(
            m.__name__ for m in iterate_modules("importing_test_package.implicit_package", recursive=False)
        ) == ["importing_test_package.implicit_package.spam"]

    def test_importing_module(self):
        assert list(m.__name__ for m in iterate_modules("pca.packages.archunit.importing")) == [
            "pca.packages.archunit.importing",
        ]

    def test_importing_funciton(self):
        with pytest.raises(OwnImportError):
            tuple(iterate_modules("pca.packages.archunit.importing:iterate_modules"))
