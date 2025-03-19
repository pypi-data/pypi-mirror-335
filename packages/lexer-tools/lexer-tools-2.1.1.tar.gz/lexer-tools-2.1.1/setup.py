from setuptools import setup, find_packages

setup(
    name="lexer-tools",  # Package name
    version="2.1.1",  # Version number
    description="A lexer-tools is a python package that help student on NLP",
    author="Sam Anderson",
    author_email="samanderson69@gmail.com",
    packages=find_packages(),  # Automatically find packages
    include_package_data=True,  # Include non-Python files
    package_data={
        "lexer_tools": [
            "data/exp1/*",
            "data/exp2/*",
            "data/exp3/*",
            "data/exp4/*",
            "data/exp5/*",
        ],  # Include all files in the data folders
    },
    install_requires=[],  # Add dependencies if needed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Python version requirement
)