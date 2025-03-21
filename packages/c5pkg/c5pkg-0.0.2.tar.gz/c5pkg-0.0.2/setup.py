from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'simple package for ai'
LONG_DESCRIPTION = 'These are my ai tools for creating chains and graphs.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="c5pkg", 
        version=VERSION,
        author="C5m7b4",
        author_email="c5m7b4@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        keywords=['python', 'first package'],
        classifiers= []
)