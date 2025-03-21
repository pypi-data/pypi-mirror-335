import os, time
from setuptools import setup, find_packages


def remove_init_files(directory):
    for root, dirs, files in os.walk(directory):
        init_path = os.path.join(root, '__init__.py')
        if os.path.exists(init_path):
            os.remove(init_path)


def generate_init_files(directory):
    for root, dirs, files in os.walk(directory):
        init_path = os.path.join(root, '__init__.py')

        if any(file.endswith(".py") for file in files): 
            with open(init_path, 'w') as init_file:
                init_file.write("")



# Ensure __init__.py is generated only in directories with .py files
remove_init_files('MatRocket')
generate_init_files('MatRocket')
with open('MatRocket\__init__.py', 'w') as init_file: init_file.write("")

setup(
    name="MatRocket",
    version="0.10.5",  # Increment your version
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