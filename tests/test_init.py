"""Tests for `pca.packages.archunit` package."""


def test_pca_namespace():
    """Test the package is accessible through the `pca` namespace"""
    from pca.packages import archunit

    assert hasattr(archunit, "VERSION")
