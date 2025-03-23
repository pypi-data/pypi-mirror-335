def is_in_ipython() -> bool:
    """Return True if running in IPython kernel, False if not."""
    try:
        from IPython import get_ipython

        if get_ipython() is None:
            return False
        else:
            return True
    except ImportError:
        return False
