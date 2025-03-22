import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="transend",
    version="0.1.0",
    author="NexaMotion Group / Transtar Industries",
    author_email="dev@transtar1.com",
    description="Python Client for the Transend Automotive Tech APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TranstarIndustries/transend-python",
    project_urls={
        "Bug Tracker": "https://github.com/TranstarIndustries/transend-python/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.1",
    ],
)
