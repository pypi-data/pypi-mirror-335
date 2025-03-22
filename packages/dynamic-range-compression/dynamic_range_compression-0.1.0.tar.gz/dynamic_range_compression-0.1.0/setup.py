from setuptools import setup, find_packages

setup(
    name='dynamic_range_compression', 
    version='0.1.0',                       
    description='Dynamic range compression in Python based on Audacity\'s and Daniel Rudrich\'s algorithm',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Joshua Jenkins',
    url='https://github.com/jjenkins2004/PythonDynamicRangeCompression',
    packages=find_packages(),               
    install_requires=[
        'numpy>=2.1.3',
        'pydub>=0.25.1',
        'numba>=0.61.0',
        'audioop-lts>=0.2.1'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.13',
)
