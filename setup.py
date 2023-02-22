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
    name="django-avatar",
    version=find_version("avatar", "__init__.py"),
    description="A Django app for handling user avatars",
    long_description=read("README.rst"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="avatar, django",
    author="Eric Florenzano",
    author_email="floguy@gmail.com",
    maintainer="Johannes Wilm",
    maintainer_email="johannes@fiduswriter.org",
    url="https://github.com/jazzband/django-avatar/",
    license="BSD",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "avatar": [
            "templates/notification/*/*.*",
            "templates/avatar/*.html",
            "locale/*/LC_MESSAGES/*",
            "media/avatar/img/default.jpg",
        ],
    },
    install_requires=[
        "Pillow>=8.4.0",
        "django-appconf>=1.0.5",
        "dnspython>=2.3.0",
    ],
    zip_safe=False,
)
