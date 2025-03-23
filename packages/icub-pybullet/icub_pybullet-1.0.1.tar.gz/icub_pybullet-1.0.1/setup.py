from setuptools import setup
from pathlib import Path
import os
import sysconfig

app_name = "icub_pybullet"
folders_to_copy = ["iCub", "other_meshes", "icub_pybullet"]
files_to_copy = []
sub_path = {}

# Get the correct site-packages path dynamically
site_packages_path = sysconfig.get_path("purelib").split("/lib/")[1]

# Collect non-Python files
for folder in folders_to_copy:
    for path in Path(folder).rglob('*'):
        if path.is_file() and path.suffix != ".pyc":
            folder_path = os.path.join("lib", site_packages_path, os.path.normpath(path.parent))
            file_path = os.path.normpath(path)
            sub_path.setdefault(folder_path, []).append(file_path)

files_to_copy.extend(sub_path.items())

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name=app_name,
    version="1.0.1",
    description="pyCub - iCub in PyBullet",
    package_dir={"": "."},
    data_files=files_to_copy,
    install_requires=install_requires,
    author="Lukas Rustler",
    author_email="lukas.rustler@fel.cvut.cz",
    url="https://www.lukasrustler.cz/pycub"
)