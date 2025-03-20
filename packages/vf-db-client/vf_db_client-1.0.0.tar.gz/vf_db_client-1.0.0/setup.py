from setuptools import setup, find_packages

setup(
    name="vf-db-client",
    version="1.0.0",
    packages=find_packages(),
    package_data={'': ['*.so']},  # Include any binary files
    install_requires=[
        "prisma-client-py>=0.7.0"
    ],
)
