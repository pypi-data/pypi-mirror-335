from setuptools import setup, find_packages

setup(
    name="pylogiless",
    version="0.2.0",
    author="LOGILESS API Python Client Contributors",
    author_email="contact@logiless.jp",
    description="Python client for the LOGILESS API",
    long_description="Python client for the LOGILESS API",
    long_description_content_type="text/markdown",
    url="https://github.com/logiless/pylogiless",
    package_dir={"": "pylogiless"},
    packages=find_packages(where="pylogiless"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    keywords="logiless, api, logistics, inventory, warehouse",
    project_urls={
        "Bug Tracker": "https://github.com/logiless/pylogiless/issues",
        "Documentation": "https://github.com/logiless/pylogiless/blob/main/docs",
        "Source Code": "https://github.com/logiless/pylogiless",
    },
)
