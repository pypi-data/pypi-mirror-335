from setuptools import setup, find_packages

setup(
    name="gosms-ru-client",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Python client for GoSMS API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gosms",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 