from setuptools import setup, find_packages

setup(
    name="aspm",
    version="0.1",
    packages=find_packages(),
    author="Aswin Venkat",
    author_email="aspm@securin.io",
    description="A python library to scan your code for vulnerabilities.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests>=2.32.3",
        "boto3>=1.34.25",
        "botocore>=1.34.25",
        "pycryptodome>=3.10.1",
        "toml>=0.10.2"
    ],
    entry_points={
        'console_scripts': [
            'aspm=aspm.scanner:main',
        ],
    },
)