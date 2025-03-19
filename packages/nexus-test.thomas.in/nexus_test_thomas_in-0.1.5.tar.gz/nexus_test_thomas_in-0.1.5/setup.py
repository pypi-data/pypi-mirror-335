from setuptools import setup, find_packages

setup(
    name='nexus_test.thomas_in',
    version='0.1.5',
    packages=find_packages(),
    description='nexus test',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='thomas.in',
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