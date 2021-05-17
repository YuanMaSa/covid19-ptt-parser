from setuptools import setup

with open('requirements.txt', 'r') as f:
    target = [x.strip() for x in f.readlines()]

setup(
    install_requires=target
)