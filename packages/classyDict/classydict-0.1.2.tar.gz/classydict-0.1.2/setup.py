from setuptools import setup, find_packages

# Read the contents of your README file
with open('readme.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='classyDict',
    version='0.1.2',
    packages=find_packages(),
    description='A dictionary that supports dot notation access, including nested dicts.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Hassan Rasool',
    author_email='hassanrasool1057@gmail.com',
    url='https://github.com/HassanRasoo98/classy-dict',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
) 
