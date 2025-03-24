from setuptools import setup, find_packages

setup(
    name="pyxpuproxy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple module to start a proxy server.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/malikuo/pyxpuproxy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
