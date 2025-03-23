import os
from setuptools import setup, find_packages

# Get the absolute path of the directory containing setup.py
here = os.path.abspath(os.path.dirname(__file__))

# Read requirements
with open(os.path.join(here, "requirements.txt")) as f:
    requirements = f.read().splitlines()

# Read PyPI description
with open(os.path.join(here, "PYPI.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="friday-ai-cli",
    version="0.1.1",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "friday=friday.main:app",
        ],
    },
    author="Yash Chouriya",
    author_email="yashchouriya131@gmail.com",
    description="FRIDAY AI CLI - Your AI-powered software development assistant built on Claude 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="cli, ai, development, assistant, claude, anthropic, coding assistant, developer tools, ai assistant",
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Documentation",
    ],
    include_package_data=True,
    zip_safe=False,
    package_data={
        "": ["PYPI.md", "requirements.txt"],
    },
)
