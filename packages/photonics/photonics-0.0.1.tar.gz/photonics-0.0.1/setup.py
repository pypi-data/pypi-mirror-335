from setuptools import setup, find_packages

setup(
    name='photonics',             # Package name
    version='0.0.1',                   # Initial version
    author='Jonah Bardos',
    author_email='',
    description='Photonics package for simulating and analyzing photonic systems',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='',  # URL to your project repository
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Update as needed
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
