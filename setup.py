from setuptools import setup, find_packages

setup(
    name="weekly_tasks_script",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
        'python-dotenv>=0.19.0',
        'markdown>=3.3.0',
    ],
    entry_points={
        'console_scripts': [
            'weekly-tasks=src.cli:main',
        ],
    },
)
