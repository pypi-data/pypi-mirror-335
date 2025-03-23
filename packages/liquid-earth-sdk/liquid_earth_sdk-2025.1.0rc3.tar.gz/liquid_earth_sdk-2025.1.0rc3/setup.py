import os
from os import path

from setuptools import setup, find_packages


def read_requirements(file_name, base_path=""):
    # Construct the full path to the requirements file
    full_path = os.path.join(base_path, file_name)
    requirements = []
    with open(full_path, "r", encoding="utf-8") as f:
        for line in f:
            # Strip whitespace and ignore comments
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            # Handle -r directive
            if line.startswith("-r "):
                referenced_file = line.split()[1]  # Extract the file name
                # Recursively read the referenced file, making sure to include the base path
                requirements.extend(read_requirements(referenced_file, base_path=base_path))
            else:
                requirements.append(line)

    return requirements


setup(
    name='liquid_earth_sdk',
    packages=find_packages(exclude=('test', 'docs', 'examples')),
    url='',
    license='EUPL-v1.2',
    author='Miguel de la Varga',
    author_email='miguel@terranigma-solutions.com',
    description='Python SDK to interact with Liquid Earth',
    install_requires=read_requirements("requirements.txt", "requirements"),
    setup_requires=['setuptools_scm'],
    use_scm_version={
            "root"            : ".",
            "relative_to"     : __file__,
            "write_to"        : path.join("liquid_earth_sdk", "_version.py"),
            "fallback_version": "0.0.1"
    },
)
