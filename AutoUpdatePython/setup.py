"""
Setup script for AutoUpdate Python package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autoupdate-python",
    version="1.0.0",
    author="AutoUpdate System",
    author_email="autoupdate@example.com",
    description="Automatic update system for Python applications from GitHub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/your-repo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "autoupdate=cli.check_updates:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
