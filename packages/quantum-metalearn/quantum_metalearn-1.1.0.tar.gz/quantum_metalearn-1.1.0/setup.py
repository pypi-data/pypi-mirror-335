from setuptools import setup, find_packages

setup(
    name="quantum-metalearn",
    version="1.1.0",
    packages=find_packages(include=["metalearn*"]),
    install_requires=[
        "torch>=2.0.0",
        "gymnasium>=0.28.0",
        "numpy>=1.23.0",
        "tqdm>=4.65.0",
        "click>=8.1.0"
    ],
    entry_points={
        'console_scripts': [
            'metalearn=metalearn.interfaces.cli:cli'
        ]
    },
    python_requires='>=3.9'
)