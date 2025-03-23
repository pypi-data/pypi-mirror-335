from setuptools import setup, find_packages

setup(
    name="zebra_analyzer_hu",
    version="1.2",
    packages=find_packages(),
    include_package_data=True,  # package_data içeriğini dahil et
    package_data={
        "zebra_analyzer_hu": ["zebra_files_hu/*"]
    },
    install_requires=[
        "pandas",
        "matplotlib",
        "adjustText"
    ],
    entry_points={
        "console_scripts": [
            "zebra-analyze=zebra_analyzer.analyzer:run_analysis"
        ]
    },
    author="Ali Sir Aydemir",
    description="Zebra Simulation Analyzer Library",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alisiraydemir/zebra_analyzer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
