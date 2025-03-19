from setuptools import setup, find_packages
VERSION = '0.0.1'
DESCRIPTION = 'My first Python package'
LONG_DESCRIPTION = 'My first Python package with a slightly longer description'
# Configuration
setup(
    # The name must match the filename'package'
    name="xiaoliupackage",
    version=VERSION,
    author="Liu",
    author_email="xaliu@edolby.com",  # Replace with your actual email
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],  # Example dependencies, modify according to actual situation
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
