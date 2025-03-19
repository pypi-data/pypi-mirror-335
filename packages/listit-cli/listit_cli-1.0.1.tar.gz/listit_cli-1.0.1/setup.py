from setuptools import setup, find_packages

setup(
    name="listit-cli",
    version="1.0.1",
    description="A simple CLI tool to log and manage tasks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="GeorgeET15",
    author_email="georgeemmanuelthomas@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    packages=find_packages(),
    install_requires=[
        "pyfiglet>=0.8.0",
        "inquirer>=3.0.0",
        "rich>=12.0.0",
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "listit = listit.listit:main",  # Updated from 'list.listit:main'
        ],
    },
)