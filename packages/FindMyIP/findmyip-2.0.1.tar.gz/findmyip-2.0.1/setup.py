from pathlib import Path
from setuptools import setup, find_packages

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text(encoding="utf-8")

# This call to setup() does all the work
setup(
    name="FindMyIP",
    version="2.0.1",
    description="Find your IP address (both internal and external) or check your connection state.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Mehran-Seifalinia/FindMyIP",
    author="Mehran Seifalinia",
    author_email="mehran.seifalinia@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
        packages=find_packages(),
    install_requires=[],
    python_requires=">=3.12",
    include_package_data=True,
)