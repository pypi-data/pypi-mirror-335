from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    description = file.read()

setup(
    name = 'super_simplex',
    long_description = description,
    long_description_content_type = 'text/markdown',
    version = '0.0.1',
    packages = find_packages(),
    install_requires = []
)