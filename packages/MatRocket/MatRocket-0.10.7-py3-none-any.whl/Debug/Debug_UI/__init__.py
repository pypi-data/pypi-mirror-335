import pkgutil
import importlib

__path__ = pkgutil.extend_path(__path__, __name__)

# Automatically import all Python files in this package
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, prefix=__name__ + "."):
    if not is_pkg:  # Ignore directories
        importlib.import_module(module_name)
