"""A setuptools module for Messages.
"""

from pathlib import Path
from setuptools import find_packages, setup

setup(
    name="macos-messages",
    version="1.0.0-beta",
    license="MIT",
    description="CLI for macOS Messages archives",
    long_description=Path("README.rst").read_text(),
    author="Constantine Kousoulis",
    author_email="constantine@kousoulis.org",
    url="https://github.com/ckousoulis/macos-messages",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "macos-messages = messages.__main__:main",
        ],
    },
    python_requires="~=3.7",
    install_requires=["xattr"],
    keywords="cli macos messages chats",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: System :: Recovery Tools",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
)
