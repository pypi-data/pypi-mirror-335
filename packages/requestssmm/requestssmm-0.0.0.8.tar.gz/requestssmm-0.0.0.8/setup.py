from setuptools import setup, find_packages

setup(
    name='requestssmm',
    version='0.0.0.8',
    packages=find_packages(),
    install_requires=[
        'requests',  'fb_atm','requestssmm','mahdix'# Replace 'some_dependency' with the actual dependency
    ],
)
