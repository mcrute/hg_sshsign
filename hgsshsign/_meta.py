# vim:filetype=python:fileencoding=utf-8

__version__ = "0.1.0"

SETUP_ARGS = dict(
    name="hg-sshsign",
    description="ssh signing for mercurial commits",
    author="Mike Crute",
    author_email="mcrute@gmail.com",
    url="http://code.google.com/p/hg-sshsign",
    license="Apache 2.0",
    version=__version__,
    packages=['hgsshsign'],
    install_requires=[
        "M2Crypto",
    ],
)
