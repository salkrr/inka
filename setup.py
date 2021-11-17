from setuptools import setup, find_packages

from src.inka import __version__

with open("README.md", mode="rt", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="inka",
    version=__version__,
    author="Kirill Salnikov",
    author_email="salnikov.k54@gmail.com",
    description="Command-line tool for adding flashcards from Markdown files to Anki",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/keiqu/inka",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    license="GPLv3",
    keywords="anki, markdown, spaced-repetition",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[
        "mistune==2.0.0rc1",
        "requests==2.26.0",
        "click==8.0.3",
        "rich==10.14.0",
    ],
    entry_points={"console_scripts": ["inka=inka.cli:cli"]},
)
