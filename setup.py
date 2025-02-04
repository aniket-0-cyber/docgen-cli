# setup.py
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
from datetime import datetime

# Read version from version.txt or default to current date-based version
def get_version():
    version = "1.0.0"
    if os.path.exists("version.txt"):
        with open("version.txt", "r") as f:
            version = f.read().strip()
    return version

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="docgen-cli",
    version=get_version(),
    author="Aniket Singh",  # Replace with your actual name
    author_email="aniket0999@gmail.com",  # Replace with your actual email
    description="AI-Powered Documentation Generator for Developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Using private GitHub repo for now
    url="https://github.com/aniket-0-cyber/docgen-cli",  # Replace with your actual private repo URL
    project_urls={
        "Bug Reports": "https://github.com/aniket-0-cyber/docgen-cli/issues",  # Private repo issues
        "Source": "https://github.com/aniket-0-cyber/docgen-cli",  # Private repo source
    },
    packages=find_packages(exclude=["tests*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    setup_requires=[
        "setuptools>=42",
        "wheel",
        "cython>=3.0.0",
    ],
    build_requires=[
        "cython>=3.0.0",
    ],
    install_requires=[
        "aiohttp>=3.8.0",
        "google-generativeai>=0.8.0",
        "google-api-python-client>=2.100.0",
        "google-auth>=2.22.0",
        "typer>=0.9.0",
        "rich>=13.3.0",
        "gitpython>=3.1.30",
        "esprima>=4.0.0",
        "javalang>=0.13.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "tqdm>=4.65.0",
        "cython>=3.0.0",
        "pydantic>=2.0.0",
        "ratelimit>=2.2.0",
        "cryptography>=38.0.0",
        "pywin32; platform_system=='Windows'",
        "python-dotenv>=1.0.1"
    ],
    extras_require={
        'dev': [
            'pytest>=8.3.4',
            'black>=24.10.0',
            'isort>=5.13.2',
            'mypy>=1.8.0',
            'pytest-cov>=4.1.0',
            'pytest-asyncio>=0.23.0',
        ]
    },
    entry_points={
        "console_scripts": [
            "docgen=docgen.cli:app",
        ],
    },
    include_package_data=True,
    keywords="documentation generator ai development tools docstring markdown",
    ext_modules=cythonize(["docgen/utils/_machine_utils.pyx"], language_level=3),
)

