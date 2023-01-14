import setuptools

setuptools.setup(
    name="googleapiclient",
    version="1.0.0",
    author="Google Inc.",
    description="Google API Client Library for Python",
    packages=setuptools.find_packages(),
    # Additional entry points for command line scripts
    entry_points={
        "console_scripts": [
            "googleapiclient_cli = googleapiclient.scripts.googleapiclient_cli:main"
        ],
    },
    install_requires=[
        "google-api-python-client",
        "googleapiclient_cli"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        
    ],
)
