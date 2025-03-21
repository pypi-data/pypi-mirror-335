from setuptools import setup, find_packages

setup(
    name="configfacets",
    version="0.0.4",
    packages=find_packages(),
    install_requires=["requests", "pyyaml"],
    description="Package for generating application configuration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Gokul Nathan",
    author_email="nathangokul111@gmail.com",
    url="https://github.com/configfacets/python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
