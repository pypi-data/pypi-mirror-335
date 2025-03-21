import pegasustools as pt


def test_times_2() -> None:
    test_var: int = 4
    assert pt.times_2(test_var) == 2 * test_var
