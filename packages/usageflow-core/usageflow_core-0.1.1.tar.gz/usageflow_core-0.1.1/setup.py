from setuptools import setup, find_namespace_packages

setup(
    name="usageflow-core",
    version="0.1.1",
    packages=find_namespace_packages(include=["usageflow.*"]),
    install_requires=[
        "requests>=2.25.0",
        "python-jwt>=4.0.0",
    ],
    author="UsageFlow",
    author_email="ronen@usageflow.io",
    description="Core functionality for UsageFlow - Usage-based pricing made simple",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/usageflow/usageflow-python",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
) 