from setuptools import setup, find_packages # type: ignore

setup(
    name='SPLDB',
    version='0.0.2',
    packages=find_packages(),
    install_requires=['dropbox'],
    author='Alpha-O-Auro SpL',
    author_email='imr@outlook.in',
    description='A Dropbox used as a Database.',
    python_requires='>=3.6',
)