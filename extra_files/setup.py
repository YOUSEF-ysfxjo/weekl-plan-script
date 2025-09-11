from setuptools import setup, find_packages

setup(
    name="weekly-tasks-script",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'pytest>=6.2.5',
        'pytest-mock>=3.6.1',
    ],
)
