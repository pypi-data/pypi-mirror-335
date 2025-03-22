from setuptools import setup, find_packages

setup(
    name="handit-sdk",  # The name users will use to install the package
    version="1.11.0",
    description="A Python SDK for tracking Model requests and responses.",
    author="Your Name",
    author_email="cristhian@handit.ai",
    url="https://github.com/Handit-AI/handit-sdk",  # Replace with your GitHub repo
    packages=find_packages(),
    install_requires=[
        "requests",
        "jsonpickle",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
