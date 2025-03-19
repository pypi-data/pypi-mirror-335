from setuptools import setup
import os

VERSION = "0.1.13"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="pl-neon-recording",
    description="pl-neon-recording is now pupil-labs-neon-recording",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["pupil-labs-neon-recording"],
    classifiers=["Development Status :: 7 - Inactive"],
)
