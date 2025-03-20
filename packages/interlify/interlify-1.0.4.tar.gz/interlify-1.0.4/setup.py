# setup.py
from setuptools import setup, find_packages

setup(
    name='interlify',           # The package name as it will appear on PyPI
    version='1.0.4',
    description='A Python client for the Interlify API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Interlify',
    author_email='eric.zhoul@interlify.com',
    url='https://github.com/EricZhou0815/Interlify-python-sdk',  # Optional, if you have a repository
    packages=find_packages(),           # Automatically find packages in the directory
    install_requires=[
        'requests',                    # List any dependencies your client requires
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update if you use a different license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
