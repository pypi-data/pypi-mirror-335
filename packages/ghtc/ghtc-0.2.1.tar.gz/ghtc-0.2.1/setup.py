from setuptools import setup
from setuptools import find_packages

with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n')
        if (line and not line.startswith('--')) and (";" not in line)]

with open("README.md") as f:
    long_description = f.read()

# Version "0.0.0" will be replaced by CI when releasing
setup(
    author="Fabien MARTY",
    author_email="fabien.marty@meteo.fr",
    name='ghtc',
    version="v0.2.1",
    license="BSD 3",
    python_requires='>=3.6',
    url="https://git.meteo.fr/dsi-dev-ws/ghtc",
    description="ghtc service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "ghtc = ghtc.cli:main",
        ]
    }
)
