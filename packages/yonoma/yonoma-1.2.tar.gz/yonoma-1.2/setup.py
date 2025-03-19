from setuptools import setup, find_packages
import os

# Correct path to version.py
version_path = os.path.join(os.path.dirname(__file__), "src", "yonoma", "version.py")

if not os.path.exists(version_path):
    raise FileNotFoundError(f"Error: version.py file not found at {version_path}")

# Read the version
version_globals = {}
with open(version_path, "r") as f:
    exec(f.read(), version_globals)

VERSION = version_globals.get("VERSION", "0.0.1")

setup(
    name="yonoma",
    version= VERSION,
    package_dir={'': 'src'}, 
    packages=find_packages(where='src'),
    install_requires=["requests"],
    author="YONOMAHQ",
    author_email="tools@yonoma.io",
    description="A Python client for the Yonoma API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YonomaHQ/yonoma-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13.2",
)
