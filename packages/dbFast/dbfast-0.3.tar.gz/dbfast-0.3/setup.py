from setuptools import setup, find_packages

setup(
    name='dbFast',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        'sqlalchemy'
    ],
    author='Vanja Nazarenko',
    email="nazareni300@gmail.com",
    description='my own library for Fast database',
)