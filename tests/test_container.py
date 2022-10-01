from pca.packages.archunit import container


def test_application_repr():
    assert repr(container.Application("application name")) == "Application(name='application name')"
