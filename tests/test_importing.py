from pca.packages.archunit.importing import iterate_modules


class TestIterateModules:
    def test_importing_implicit_package(self):
        assert list(m.__name__ for m in iterate_modules("importing_test_package")) == [
            "importing_test_package.implicit_package.implicit_subpackage.bar.baz",
            "importing_test_package.implicit_package.implicit_subpackage.bar.quax",
            "importing_test_package.implicit_package.implicit_subpackage.bar.tests.standalone_test_module",
            "importing_test_package.implicit_package.implicit_subpackage.foo",
        ]

    def test_importing_module(self):
        assert list(m.__name__ for m in iterate_modules("pca.packages.archunit.importing")) == [
            "pca.packages.archunit.importing",
        ]
