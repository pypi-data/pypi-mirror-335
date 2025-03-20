from setuptools import setup, find_packages

VERSION = '1.1.2'
DESCRIPTION = 'An easy and fun encryption module.'
LONG_DESCRIPTION = open('README.md').read()

setup(
        name="sweecrypt", 
        version=VERSION,
        author="SweeZero",
        author_email="meow@swee.codes",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
        ]
)
