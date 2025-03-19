from setuptools import setup, find_packages
import os

def generate_init_files(package_dir):
    for root, dirs, files in os.walk(package_dir):
        if "__init__.py" not in files:
            with open(os.path.join(root, "__init__.py"), "w", encoding="utf-8") as f:
                f.write("from pkgutil import extend_path\n")
                f.write("__path__ = extend_path(__path__, __name__)\n\n")

        # Automatically import all submodules
        submodules = [f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"]
        if submodules:
            with open(os.path.join(root, "__init__.py"), "a", encoding="utf-8") as f:
                for submodule in submodules:
                    f.write(f"from . import {submodule}\n")

# 🔹 Run the function before building the package
generate_init_files("MatRocket")

setup(
    name="MatRocket",
    version="0.7",
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