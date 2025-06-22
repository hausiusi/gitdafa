from setuptools import setup, find_packages

setup(
    name='gitdafa',
    version='0.8.0',
    author='Zviad Mgaloblishvili, Irakli Sivsivadze',
    description='Gitdafa is a handy tool designed for analyzing contributions and activity in git projects.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hausiusi/gitdafa',
    packages=find_packages(),
    install_requires=[
        'atomicwrites==1.4.0',
        'attrs==20.3.0',
        'colorama==0.4.4',
        'iniconfig==1.1.1',
        'packaging==20.8',
        'pluggy==0.13.1',
        'py==1.10.0',
        'pyparsing==2.4.7',
        'pytest==6.2.1',
        'python-dateutil==2.8.1',
        'six==1.15.0',
        'tabulate==0.8.7',
        'toml==0.10.2',
        'yapf==0.30.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    entry_points={
    'console_scripts': [
        'gitdafa = gitdafa.run:main',
    ],
    },
    python_requires='>=3.7',
)