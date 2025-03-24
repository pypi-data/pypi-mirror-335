from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gosms-ru-client",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    author="GoSMS",
    author_email="support@gosms.ru",
    description="Python client for GoSMS API - сервис отправки SMS сообщений",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gosms.ru",
    project_urls={
        "Documentation": "https://docs.gosms.ru",
        "Source": "https://github.com/gosms/gosms-python-client",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7",
    keywords="sms, gosms, api, client, messaging",
) 