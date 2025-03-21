import importlib.metadata

import pegasustools as pt


def test_version() -> None:
    assert importlib.metadata.version("pegasustools") == pt.__version__
