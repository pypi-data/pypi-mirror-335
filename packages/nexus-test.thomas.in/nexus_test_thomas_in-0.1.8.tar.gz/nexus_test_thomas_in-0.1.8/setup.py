import os
from setuptools import setup, find_packages

def read(filepath):
    # don't die on files that may go missing due to zipping
    if os.path.exists(filepath):
        return open(filepath).read()
    return ''

setup(
    name='nexus_test.thomas.in',
    version='0.1.8',
    packages=find_packages(),
    description='nexus test',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='thomas.in',
    license=read('LICENSE'),
    author_email='thomas.in@osckorea.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django==5.0',
        'requests',  
        'numpy',     
    ],
    python_requires='>=3.6',
)