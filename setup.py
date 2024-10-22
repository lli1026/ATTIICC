# setup.py


from setuptools import setup, find_packages

setup(
    name="ATTIICCpackage",
    version="0.1.0",
    packages=find_packages(include=['ATTIICCpackage', 'ATTIICCpackage.*']),  # Adjust this to your package names
    install_requires=[],
    author="Lie Li",
    author_email="liel@uchicago.edu",
    description="A package for ATTIICC project",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
