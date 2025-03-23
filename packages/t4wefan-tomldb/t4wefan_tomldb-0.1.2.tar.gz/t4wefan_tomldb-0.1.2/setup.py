from setuptools import setup, find_packages

setup(
    name='t4wefan-tomldb',
    version='0.1.1',
    author='t4wefan',
    author_email='guanghoushi@gmail.com',
    description='A simple key-value database using TOML',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://git.t4wefan.pub/t4wefan/toml-db',
    packages=find_packages(),
    install_requires=[
        'toml',
        'filelock',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
