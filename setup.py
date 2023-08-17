from setuptools import find_packages, setup

setup(
    name="QuickSight Sync",
    packages=find_packages(),
    version="1.0.0",
    description=("QuicksightSync is a command-line tool for seamless export "+"and import of analyses and assets within AWS QuickSight instances."),
    author="Dim Kharitonov",
    author_email="dimds@fastmail.com",
    license="MIT License",
    python_requires=">=3.9",
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'qss = src.quicksight_sync:main',
        ],
    },
)
