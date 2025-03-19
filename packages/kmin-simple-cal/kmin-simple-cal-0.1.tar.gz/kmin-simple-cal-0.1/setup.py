from setuptools import setup, find_packages

setup(
    name='kmin-simple-cal',
    version='0.1',
    packages=find_packages(),
    description='A simple calculator',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='kmin4',
    author_email='kmin.kim@osckorea.com',
    url='https://github.com/kmin4/kmin-simple-cal',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
