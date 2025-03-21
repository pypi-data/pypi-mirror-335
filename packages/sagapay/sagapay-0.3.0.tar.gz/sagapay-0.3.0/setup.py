from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sagapay",
    version="0.3.0",
    author="SagaPay Team",
    author_email="support@sagapay.net",
    description="Python SDK for SagaPay - The world's first free, non-custodial blockchain payment gateway",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sagapay/sagapay-python",
    project_urls={
        "Bug Tracker": "https://github.com/sagapay/sagapay-python/issues",
        "Documentation": "https://sagapay.net/docs",
        "Source Code": "https://github.com/sagapay/sagapay-python",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=2.0.0",
    ],
    keywords="blockchain, payment, cryptocurrency, api, gateway, sagapay",
)