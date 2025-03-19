"""Package lbCta"""

try:
    import importlib.metadata

    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = f"{__name__} not versioned"
