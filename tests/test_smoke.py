import traffic_agent


def test_version():
    assert traffic_agent.__version__ == "2.0.0"


def test_package_docstring():
    assert "SPEC v2.0" in traffic_agent.__doc__
