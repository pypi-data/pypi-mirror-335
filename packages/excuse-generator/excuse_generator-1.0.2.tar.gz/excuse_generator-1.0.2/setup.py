from setuptools import setup, find_packages

setup(
    name="excuse_generator",
    version="1.0.2",
    author="Pyckle Jar",
    description="A fun excuse generator for software engineers and devs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/software-students-spring2025/3-python-package-pyckle-jar", 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "excuse-gen=excuse_generator.__main__:main",
        ]
    },
)
