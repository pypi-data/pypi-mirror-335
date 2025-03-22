import os, time
from setuptools import setup, find_packages

# Content for auto-generated __init__.py files
INIT_CONTENT = """\
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
"""

def generate_init_files(package_dir):
    """
    Ensures that each folder in package_dir has an __init__.py file that imports
    functions/classes directly from Python files inside it.
    """
    for root, dirs, files in os.walk(package_dir):
        # Only create __init__.py if the folder contains .py files
        if any(file.endswith(".py") and file != "__init__.py" for file in files):
            init_path = os.path.join(root, "__init__.py")

            # Create new __init__.py
            with open(init_path, "w", encoding="utf-8") as f:
                f.write(INIT_CONTENT)


def remove_init_files(directory):
    for root, dirs, files in os.walk(directory):
        init_path = os.path.join(root, '__init__.py')
        if os.path.exists(init_path):
            os.remove(init_path)


# Ensure __init__.py is generated only in directories with .py files
remove_init_files('MatRocket')
generate_init_files('MatRocket')
#with open('MatRocket\__init__.py', 'w') as init_file: init_file.write("")

setup(
    name="MatRocket",
    version="0.10.8",  # Increment your version
    packages=find_packages(where="MatRocket"),  # Start looking in MatRocket/MatRocket/
    package_dir={"": "MatRocket"},  # Maps package root to MatRocket/
    include_package_data=True,  # Important for non-Python files
    install_requires=[],
    author="Vilgot Lötberg",
    author_email="vilgotl@kth.se",  # Your email
    long_description=open("README.md").read(),  # A long description (from README.md)
    long_description_content_type="text/markdown",  # Specifies the format of the long description
    url="https://github.com/spiggen/MatRocket",  # Link to the package repository (e.g., GitHub)
    description="MatRocket is a library for simulating rockets in MATLAB, and provides solutions for rendering said simulations in Blender.",
    python_requires=">=3.6",
)