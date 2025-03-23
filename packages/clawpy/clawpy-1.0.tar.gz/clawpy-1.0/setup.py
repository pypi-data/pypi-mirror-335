from setuptools import setup, find_packages

setup(
    name="clawpy",  # Package name (pip install clawpy)
    version="1.0",  # Update this for new versions
    author="Anish Chaudhuri",
    author_email="studiosprimora@gmail.com",
    description="The Ultimate Free Math, AI, Physics, and Cryptography Framework.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
