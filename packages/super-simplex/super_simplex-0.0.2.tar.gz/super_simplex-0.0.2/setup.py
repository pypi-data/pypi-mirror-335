from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    description = file.read()

setup(
    name = 'super_simplex',
    long_description = description,
    long_description_content_type = 'text/markdown',
    version = '0.0.2',
    packages = find_packages(),
    install_requires = [],
    license='CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
)