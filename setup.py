from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pandas_drf_tools',
    version='0.1.1',
    description='A set of tools to make Pandas easy to use with Django REST Framework projects',
    long_description=long_description,
    url='https://github.com/abarto/pandas-drf-tools',
    author='Agustin Barto',
    author_email='abarto@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    keywords='pandas djangorestframework django',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'pandas>=0.18.1',
        'djangorestframework>=3.4.6'
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'flake8', 'nose']
    }
)
