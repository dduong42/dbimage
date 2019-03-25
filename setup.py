import re

from setuptools import find_packages, setup

with open('dbimage/__init__.py') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='dbimage',
    version=version,
    author='Daniel Duong',
    author_email='daniel.duong@outlook.com',
    description="A model to store images in the database",
    packages=find_packages(),    
    install_requires=[
        'django',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
