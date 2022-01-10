from setuptools import setup

setup(
    name='fuzzy_join',
    version='0.0.1',
    license='MIT',
    description='A small Python package that join 2 Pandas DataFrame using fuzzy matching by calculating the Levenshtein distance',
    url='https://github.com/truonghm/fuzzy_join',
    author='Truong Hoang',
    author_email='hmtrg@outlook.com',
    packages=['fuzzy_join'],
    install_requires=['pandas>=1.3.1',
                      'numpy>=1.21.1',
                      'jellyfish>=0.8.8'                     
                      ]
)
