from setuptools import setup, find_packages

setup(
    name='isoddeven',
    version='1.1.0',
    description='A Python package to check if a number is odd or even.',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='Nilay Sarma',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "isoddeven=isoddeven.cli:main",
        ],
    },
    license="MIT",
    url="https://github.com/nilaysarma/isoddeven",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Repository": "https://github.com/nilaysarma/isoddeven",
        "Release Notes": "https://github.com/nilaysarma/isoddeven/releases/latest",
    }
)