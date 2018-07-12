def test(verbose=True):
    r"""Run tests to verify this package's integrity.

    Parameters
    ----------
    verbose : bool
        ``True`` to show diagnostic. Defaults to ``True``.

    Returns
    -------
    int
        Exit code: ``0`` for success.
    """
    import pandas as pd

    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 79)
    pd.set_option("display.max_rows", 60)
    pd.set_option("display.large_repr", "truncate")

    args = ["--doctest-modules"]
    if not verbose:
        args += ["--quiet"]

    args += ["--pyargs", __name__.split(".")[0]]

    return __import__("pytest").main(args)
