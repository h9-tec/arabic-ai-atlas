import atlas


def test_atlas_import():
    """Test that atlas module can be imported."""
    assert atlas is not None


def test_atlas_version():
    """Test that atlas has correct version."""
    assert atlas.__version__ == "0.1.0"
