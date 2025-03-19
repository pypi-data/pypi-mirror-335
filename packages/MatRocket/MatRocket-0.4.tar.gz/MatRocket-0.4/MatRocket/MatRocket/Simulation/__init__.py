import pkgutil
__path__ = pkgutil.extend_path(__path__, __name__)  # Enable namespace packages

# Automatically import all submodules
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__, __name__ + "."):
    __import__(module_name)
