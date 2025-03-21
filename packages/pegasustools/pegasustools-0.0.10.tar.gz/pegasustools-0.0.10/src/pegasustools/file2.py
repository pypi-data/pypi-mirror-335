import pegasustools.file1 as pt_1


def times_6(x: int) -> int:
    """Multiply input integer by 6

    Parameters
    ----------
    x : int
        the number to multiply

    Returns
    -------
    int
        6*x
    """
    return 3 * pt_1.times_2(x)
