#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import Command, setup

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "src", "bytestkit", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)


# What packages are required for this module to be executed?
install_requires = ["tinydb", "requests", "redis", "colorlog", "pymysql", "dbutils", "nacos-sdk-python", "pycryptodome"]
tests_require = ["pytest"]

# What packages are optional?
extras_requires = {
    # 'fancy feature': ['django'],
}


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = about["__description__"]


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload --verbose dist/* ")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


if len(sys.argv) > 1 and sys.argv[1] == "publish":
    os.system("rm -f dist/ build/ bytestkit.egg-info/")
    os.system("python3 setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

# Where the magic happens:
setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    python_requires=">=3.10",
    url="",
    package_dir={"": "src"},
    packages=["bytestkit"],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_requires,
    include_package_data=True,
    license=about["__license__"],
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
