from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="plcg",
    version="1.0.1",
    author="Spencer Perkins",
    author_email="spencer.perkins44sp@gmail.com",
    description="Computational biology and machine learning utilities for the Pardee Lab Computation Group",
    project_urls={
        "Code": "https://github.com/Pardee-Lab-Computation-Group/plcg",
        "Bug Tracker": "https://github.com/Pardee-Lab-Computation-Group/plcg/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(
        where="src",
        include=["plcg*"],
    ),
    package_dir={"": "src"},
    python_requires=">=3.10",
    long_description_content_type="text/markdown",
    long_description="A variety of python utilities for biology",
    install_requires=["pandas==2.2.0", "numpy==1.26.3", "python-Levenshtein==0.23.0"],
)
