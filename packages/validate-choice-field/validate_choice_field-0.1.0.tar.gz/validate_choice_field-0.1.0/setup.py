from setuptools import setup, find_packages

setup(
    name="validate_choice_field",  # Unique package name (must be available on PyPI)
    version="0.1.0",  # Initial version
    author="muhammed gassali",
    author_email="gassalirgc@gmail.com",
    description="It is a Python package that allows users to validate a post value against the choices defined in a Django model choice field and returns the corresponding choice data for database storage.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_package",
    packages=find_packages(),
    install_requires=[],  # Add dependencies here
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
