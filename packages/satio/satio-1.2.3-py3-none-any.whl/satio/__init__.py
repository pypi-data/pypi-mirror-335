try:
    import satio.layers  # NOQA
except Exception:
    # skip error in make recipes that need version outside dev env
    pass

from satio._version import __version__

__all__ = ['__version__']
