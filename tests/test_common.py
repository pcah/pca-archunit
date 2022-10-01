from pca.packages.archunit import common


def test_tags_repr():
    assert repr(common.Tags("name for the tag")) == "Tags('name for the tag')"


def test_tags_extending():
    t1 = common.Tags("tag1")
    t2 = common.Tags("tag2")
    result = t1.update(t2)
    assert repr(result) == "Tags('tag1', 'tag2')"
    assert result is not t1
    assert result is not t2
