from setuptools import setup, find_packages
import os

def create_init_py(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        if '__init__.py' not in filenames:
            with open(os.path.join(dirpath, '__init__.py'), 'w'):
                pass  # Creates an empty __init__.py file

# Automatically generate __init__.py files in the MatRocket package
create_init_py('MatRocket')


setup(
    name="MatRocket",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,  # Important: Enables including non-Python files
    install_requires=[],
    author="Vilgot Lötberg",
    author_email="your.email@example.com",  # Your email
    long_description=open("README.md").read(),  # A long description (from README.md)
    long_description_content_type="text/markdown",  # Specifies the format of the long description
    url="https://github.com/spiggen/MatRocket",  # Link to the package repository (e.g., GitHub)
    description="MatRocket is a library for simulating rockets in MATLAB, and render provides solutions for rendering said simulations in Blender.",
    python_requires=">=3.6",
)