from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from . import MatlabBlenderIO

import importlib
def __getattr__(name):
    mod = importlib.import_module(f'{__name__}.{name}')
    return mod
