from setuptools import setup, find_packages

setup(
    name="simple-math-ss",  # This will be the name of your package on PyPI
    version="0.1.0",
    author="Savio",
    author_email="saviosebastiankann@gmail.com",
    description="A simple Python package to add one to a given number",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/yourusername/simple-math",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
