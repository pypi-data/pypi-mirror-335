import pkgutil
import importlib

__path__ = pkgutil.extend_path(__path__, __name__)

# Import all functions/classes directly
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    if not is_pkg:
        module = importlib.import_module(module_name)
        for attr in dir(module):
            if not attr.startswith("_"):  # Ignore private attributes
                globals()[attr] = getattr(module, attr)
