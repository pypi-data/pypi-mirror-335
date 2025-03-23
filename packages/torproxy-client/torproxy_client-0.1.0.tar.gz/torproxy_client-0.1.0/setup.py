from setuptools import setup, find_packages

setup(
    name='torproxy_client',
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    description='A simple Python library to connect to the internet through Tor proxy.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='mi8bi',
    author_email='mi8biiiii@gmail.com',
    url='https://github.com/mi8bi/torproxy_client',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'requests',
        'stem',
        'PySocks',
    ],
)
