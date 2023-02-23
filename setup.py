import codecs
import re
from os import path

from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    packages=find_packages(exclude=["tests"]),
    package_data={
        "avatar": [
            "templates/notification/*/*.*",
            "templates/avatar/*.html",
            "locale/*/LC_MESSAGES/*",
            "media/avatar/img/default.jpg",
        ],
    },
    zip_safe=False,
)
