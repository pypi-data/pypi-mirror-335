from setuptools import setup, find_packages
import os

def read_version():
    with open(os.path.join(os.path.dirname(__file__), 'docsplit', 'VERSION')) as f:
        return f.read().strip()

setup(
    name='docsplit',
    version=read_version(),
    packages=find_packages(),
    install_requires=[
        'pyvips',
        'pillow',
        'pypdf2',
    ],
    python_requires='>=3.6',
    package_data={
        'docsplit': ['VERSION'],
    },
)