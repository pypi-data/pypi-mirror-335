from setuptools import setup, find_packages
import os

# Auto-generate __init__.py in every subpackage
def ensure_init_files(package_dir):
    init_content = '''\
import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)

# Define a function to lazily import submodules when accessed
def __getattr__(name):
    import importlib
    return importlib.import_module(f"{__name__}.{name}")
'''

    for root, dirs, files in os.walk(package_dir):
        if "__init__.py" in files:
            init_path = os.path.join(root, "__init__.py")
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(init_content)

# Ensure all __init__.py files are updated before building the package
ensure_init_files("MatRocket")

setup(
    name="MatRocket",
    version="0.6",
    packages=find_packages(include=["MatRocket", "MatRocket.*"]),
    include_package_data=True,  # Important: Enables including non-Python files
    install_requires=[],
    author="Vilgot Lötberg",
    author_email="your.email@example.com",  # Your email
    long_description=open("README.md").read(),  # A long description (from README.md)
    long_description_content_type="text/markdown",  # Specifies the format of the long description
    url="https://github.com/spiggen/MatRocket",  # Link to the package repository (e.g., GitHub)
    description="MatRocket is a library for simulating rockets in MATLAB, and provides solutions for rendering said simulations in Blender.",
    python_requires=">=3.6",
)