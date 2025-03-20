from setuptools import setup, find_packages
import os

# 🔹 Function to remove old __init__.py files and regenerate them
def generate_init_files(package_dir):
    for root, dirs, files in os.walk(package_dir):
        init_path = os.path.join(root, "__init__.py")

        # 🔥 Remove existing __init__.py file if it exists
        if os.path.exists(init_path):
            os.remove(init_path)

        # 📌 Create a fresh __init__.py
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("from pkgutil import extend_path\n")
            f.write("__path__ = extend_path(__path__, __name__)\n\n")

            # Automatically import all submodules
            submodules = [f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"]
            for submodule in submodules:
                f.write(f"from . import {submodule}\n")

            # Also make sub-packages importable
            for subpackage in dirs:
                f.write(f"from . import {subpackage}\n")

# 🔹 Run the function before building the package
generate_init_files("MatRocket")



setup(
    name="MatRocket",
    version="0.10.1",
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