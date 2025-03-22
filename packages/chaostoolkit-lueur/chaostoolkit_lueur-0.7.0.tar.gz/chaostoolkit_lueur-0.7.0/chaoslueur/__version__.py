from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("chaostoolkit-lueur")
except PackageNotFoundError:
    __version__ = "unknown"
