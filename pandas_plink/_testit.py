def test(verbose=True):
    """
    Run tests to verify this package's integrity.

    Parameters
    ----------
    verbose : bool
        :const:`True` to show diagnostic. Defaults to :const:`True`.

    Returns
    -------
    int
        Exit code: :const:`0` for success.
    """
    from .conftest import setup_tests_baseline

    setup_tests_baseline()

    args = ["--doctest-modules"]
    if not verbose:
        args += ["--quiet"]

    args += ["--pyargs", __name__.split(".")[0]]

    return __import__("pytest").main(args)
