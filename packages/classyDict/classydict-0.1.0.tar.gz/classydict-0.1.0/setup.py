from setuptools import setup, find_packages

setup(
    name='classyDict',
    version='0.1.0',
    packages=find_packages(),
    description='A dictionary that supports dot notation access, including nested dicts.',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/classyDict',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
) 