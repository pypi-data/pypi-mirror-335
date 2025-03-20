from setuptools import setup, find_packages
import os

def generate_init_files(package_dir):
    """
    Automatically generates __init__.py files to make every directory a package.
    Each Python file becomes a submodule, and each function/class is directly importable.
    """
    for root, dirs, files in os.walk(package_dir):
        # Skip folders without Python files
        if not any(f.endswith(".py") and f != "__init__.py" for f in files):
            continue  

        init_path = os.path.join(root, "__init__.py")
        
        with open(init_path, "w", encoding="utf-8") as f:
            f.write("from pkgutil import extend_path\n")
            f.write("__path__ = extend_path(__path__, __name__)\n\n")
            
            # Import every Python file as a submodule
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    module_name = os.path.splitext(file)[0]
                    f.write(f"from . import {module_name}\n")
            
            # Auto-import all functions & classes in each module
            f.write("\nimport importlib\n")
            f.write("def __getattr__(name):\n")
            f.write("    mod = importlib.import_module(f'{__name__}.{name}')\n")
            f.write("    return mod\n")

# Ensure all __init__.py files are correctly generated before packaging
generate_init_files("MatRocket")



setup(
    name="MatRocket",
    version="0.10.2",
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