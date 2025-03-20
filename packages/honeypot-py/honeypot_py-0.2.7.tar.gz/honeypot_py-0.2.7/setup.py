from setuptools import setup, find_packages

setup(
    name="honeypot-py",
    version="0.2.7",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "cryptography",
    ],
    author="Honeypot",
    author_email="support@honeypot.run",
    description="A simple client for tracking events and user behavior",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/honeypot-run/honeypot-py",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)