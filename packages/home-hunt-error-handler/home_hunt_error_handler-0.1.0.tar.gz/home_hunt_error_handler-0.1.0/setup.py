from setuptools import setup, find_packages

setup(
    name='home_hunt_error_handler',
    version='0.1.0',
    author='Nikhil Dhoke',
    author_email='nikhildhoke1995@example.com',
    description='A custom library for handling errors in real estate application Home Hunt.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nikhildhoke/home_hunt_error_handler',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    install_requires=[
        'boto3',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
