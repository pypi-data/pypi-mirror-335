from setuptools import setup, find_packages

setup(
    name="ext_llm",
    version="0.1.16",
    description="A wrapper library to abstract common llm providers",
    author="Giovanni Pio Grieco",
    author_email="gio.grieco@stud.uniroma3.it",
    license="GPL-3.0",
    packages=find_packages(),  # Automatically find and include all packages
    install_requires=[
        # List your dependencies here
        "pyyaml",
        "boto3",
        "botocore",
        "groq"
    ],
    url="https://github.com/giovanni-grieco/ext_llm",
)