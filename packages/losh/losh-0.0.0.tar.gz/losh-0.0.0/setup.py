from setuptools import setup, find_packages

setup(
    name="losh",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[],
    author="attentionmech",
    author_email="attentionmech@example.com",
    description="losh package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/attentionmech/losh",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
