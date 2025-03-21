import pegasustools as pt


def test_times_6() -> None:
    test_var: int = 4
    assert pt.times_6(test_var) == 6 * test_var
