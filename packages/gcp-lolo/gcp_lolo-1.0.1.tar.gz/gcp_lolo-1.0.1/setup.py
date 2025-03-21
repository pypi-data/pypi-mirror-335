import os
from setuptools import setup, find_packages
from gcp_lolo import __version__

with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
    requirements = f.read().splitlines()
    print(requirements)

setup(
    name="gcp-lolo",
    version=__version__,
    packages=find_packages(),
    description="A Python package for storing application logs in GCP Cloud Logging.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Gianfranco Reppucci, ufirst",
    author_email="gianfranco.reppucci@ufirst.com",
    url="https://github.com/qurami/gcp-lolo",
    license="MIT",
    keywords=["logging", "GCP", "Cloud Logging"],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Utilities",
    ],
)
