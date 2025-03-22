import os
from setuptools import setup, find_packages


EXCLUDED_DIRS = {".git", "__pycache__"}

def generate_init_files(package_dir):
    """
    Recursively generates __init__.py files in all package directories,
    automatically importing functions/classes from submodules and subdirectories.
    Excludes non-package directories like .git, __pycache__, and .egg-info.
    """
    # Traverse all directories and subdirectories
    for root, dirs, files in os.walk(package_dir):
        # Filter out unwanted directories (e.g., .git, __pycache__, *.egg-info)
        dirs[:] = [d for d in dirs if not d.endswith(".egg-info") and d not in EXCLUDED_DIRS]
        
        # Ensure there's an __init__.py file in the current directory
        init_path = os.path.join(root, "__init__.py")
        
        # Skip if it's a non-Python directory
        if "__init__.py" not in files:
            with open(init_path, "w") as f:
                pass  # Just create an empty __init__.py file initially

        # Extract all .py module files (excluding __init__.py)
        module_files = [f[:-3] for f in files if f.endswith(".py") and f != "__init__.py"]

        # If there are module files, we need to import them into the __init__.py
        if module_files:
            with open(init_path, "w") as f:
                for module in module_files:
                    f.write(f"from .{module} import *\n")  # Import all from each module

        # Specifically handle the subdirectories in this folder
        subdirectory_files = [d for d in dirs if os.path.isdir(os.path.join(root, d))]
        for subdir in subdirectory_files:
            subdir_init_path = os.path.join(root, subdir, "__init__.py")
            if not os.path.exists(subdir_init_path):  # Ensure the subdirectory also has an __init__.py file
                with open(subdir_init_path, "w") as f:
                    pass  # Create an empty __init__.py file for subdirectories

            # Append imports for the subdirectories in the parent __init__.py file
            with open(init_path, "a") as f:
                f.write(f"from .{subdir} import *\n")  # Import all subdirectories


def remove_init_files(directory):
    for root, dirs, files in os.walk(directory):
        init_path = os.path.join(root, '__init__.py')
        if os.path.exists(init_path):
            os.remove(init_path)


remove_init_files('MatRocket')
generate_init_files('MatRocket')




setup(
    name="MatRocket",
    version="0.10.12",  # Increment your version
    packages=find_packages(),  # Start looking in MatRocket/MatRocket/
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