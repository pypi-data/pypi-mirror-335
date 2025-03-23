from setuptools import setup, find_packages
import os

# Load version from version.txt
with open(os.path.join("goodvirus", "version.txt"), "r") as f:
    version = f.read().strip()

setup(
    name="goodvirus",
    version=version,
    author="Nico",
    author_email="",
    description="An ethical, self-updating system watchdog daemon that alerts users of suspicious behavior.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/goodvirus/",  # Update this after upload
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "psutil",
        "configparser"
    ],
    entry_points={
        "console_scripts": [
            "goodvirus = goodvirus.observer:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
