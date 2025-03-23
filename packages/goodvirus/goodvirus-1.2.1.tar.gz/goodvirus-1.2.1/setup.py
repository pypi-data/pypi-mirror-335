from setuptools import setup, find_packages

# Load metadata from goodvirus/__about__.py
about = {}
with open("goodvirus/__about__.py", encoding="utf-8") as f:
    exec(f.read(), about)

# Read README for long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about.get("__email__", ""),
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/goodvirus/",
    license=about["__license__"],
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
