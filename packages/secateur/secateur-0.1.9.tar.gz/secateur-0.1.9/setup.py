from setuptools import setup, find_packages

def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()

setup(
    name='secateur',
    version='0.1.9',
    packages=find_packages(),
    package_data={'secateur': ['schema.json']},
    install_requires=read_requirements('requirements.txt'),
    author='Daniil Somov',
    author_email='darenty4@gmail.com',
    description='A framework for migrating relational databases to document-oriented databases',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/darentydarenty/secateur',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)