from setuptools import setup, find_packages

setup(
    name="aws-cdk-secure-modules",
    version="0.1.0",
    packages=find_packages(include=["constructs*", "tests*"]),
    install_requires=["aws-cdk-lib", "constructs", "pytest"],
    python_requires=">=3.12",
)
