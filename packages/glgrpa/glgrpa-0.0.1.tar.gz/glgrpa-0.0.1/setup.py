# setup.py
from setuptools import setup, find_packages

setup(
    name='glgrpa',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'pandas',
    ],
    description='Librería para automatización de tareas en RPA dentro de Grupo Los Grobo',
    author='Bellome, Gabriel <gabriel.bellome@losgrobo.com>',
    author_email='gabriel.bellome@losgrobo.com',
    url='https://GrupoLosGrobo@dev.azure.com/GrupoLosGrobo/GrupoLosGrobo%20RPA/_git/GrupoLosGrobo%20RPA',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)