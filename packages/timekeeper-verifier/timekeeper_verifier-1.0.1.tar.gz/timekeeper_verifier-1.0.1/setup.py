
from setuptools import setup, find_packages

PACKAGE = "timekeeper_verifier"
DESCRIPTION = "timekeeper verifier"
AUTHOR = "ajbucddd"
VERSION = '1.0.1'
with open("README.md", "r") as fh:
    long_description = fh.read()

setup_args = {
    'version': VERSION,
    'description': DESCRIPTION,
    'author': AUTHOR,
    'license': "Apache License 2.0",
    'packages': find_packages(exclude=["tests*"]),
    'long_description': long_description,
    'long_description_content_type': "text/markdown",
    'platforms': 'any',
    'python_requires': '>=3.6',
    'classifiers': (
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development',
    )
}

setup(name='timekeeper-verifier', **setup_args)
