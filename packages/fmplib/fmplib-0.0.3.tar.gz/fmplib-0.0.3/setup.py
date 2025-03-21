from setuptools import find_packages, setup

setup(
    name='fmplib',
    packages=find_packages(include=['fmplib', 'fmplib.*']),
    version='0.0.3',
    description='Library to access Financial Modeling Prep API',
    author='AlgoÉTS',
    install_requires=["python-dotenv",
                      "requests"]
)
