import os, time
from setuptools import setup, find_packages


def generate_init_files(package_dir):
    """
    Recursively generates __init__.py files in all package directories,
    automatically importing functions/classes from submodules.
    """
    for root, dirs, files in os.walk(package_dir):
        if "__init__.py" not in files:  # Ensure there's an __init__.py
            init_path = os.path.join(root, "__init__.py")
            with open(init_path, "w") as f:
                pass  # Create an empty __init__.py file

        # Extract all .py module files (excluding __init__.py)
        module_files = [f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"]

        if module_files:
            init_path = os.path.join(root, "__init__.py")
            with open(init_path, "w") as f:
                for module in module_files:
                    f.write(f"from .{module} import *\n")  # Import all from each module

def remove_init_files(directory):
    for root, dirs, files in os.walk(directory):
        init_path = os.path.join(root, '__init__.py')
        if os.path.exists(init_path):
            os.remove(init_path)


remove_init_files('MatRocket')
generate_init_files('MatRocket')




setup(
    name="MatRocket",
    version="0.10.10",  # Increment your version
    packages=find_packages(where="MatRocket", include=["MatRocket.*"]),  # Start looking in MatRocket/MatRocket/
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