from setuptools import setup, find_packages

setup(
    name="syspro-sdk",
    version="0.1.2",
    license='Commercial',
    author="Vincent Goineau",
    author_email="vincent@heyvince.co",
    description="A Python package for Syspro API interactions",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "httpx",
        "xmltodict",
        "jsonpath-ng",
        "pandas" # Add dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: Other/Proprietary License',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8'
)
