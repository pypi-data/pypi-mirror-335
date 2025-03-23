from setuptools import setup, find_packages
import os

def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name), encoding='utf-8') as f:
        return f.read()

setup(
    name="doc2txt-antiword",  # Updated name for more clarity and distinctiveness
    version="0.1.0",
    author="Bhola Kumar",
    author_email="bholak993@example.com",
    description="A Python package to convert .doc files to .txt using the Antiword binary.",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/Bhola-kumar/doc2txt-py",  # Replace with your actual repo URL
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'doc2txt': ['bin/antiword/antiword.exe'],  # Ensure the binary is included in the package
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],  # Add any dependencies your package needs, e.g., 'requests'
)
