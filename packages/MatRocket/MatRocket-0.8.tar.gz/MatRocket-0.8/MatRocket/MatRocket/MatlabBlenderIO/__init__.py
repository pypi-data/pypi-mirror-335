import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)

# Define a function to lazily import submodules when accessed
def __getattr__(name):
    import importlib
    return importlib.import_module(f"{__name__}.{name}")
from . import MatlabBlenderIO
from . import MatlabBlenderIO
