from setuptools import setup

setup(
    name='cgstep',
    version='1.6',
    description='Python package and command line tool to control stepping motor driver RPZ-Stepper/TMC5240 on Raspberry Pi',
    author='Indoor Corgi',
    author_email='indoorcorgi@gmail.com',
    url='https://github.com/IndoorCorgi/cgstep',
    license='Apache License 2.0',
    packages=['cgstep'],
    install_requires=[],
    entry_points={'console_scripts': ['cgstep=cgstep:cli',]},
    python_requires='>=3.9',
)
