from setuptools import setup
from hgsshsign import __version__


setup(
    name="hg-sshsign",
    description="ssh signing for mercurial commits",
    author="Mike Crute",
    author_email="mcrute@gmail.com",
    url="http://code.google.com/p/hg-sshsign",
    license="Apache 2.0",
    version=__version__,
    install_requires=[
        "M2Crypto",
    ])
