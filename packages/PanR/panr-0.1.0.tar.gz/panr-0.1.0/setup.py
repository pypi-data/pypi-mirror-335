from setuptools import setup

setup(
    name="PanR",
    version="0.1.0",
    author="Tasnimul Arabi Anik",
    author_email="arabianik987@gmail.com",
    description="A Python tool for panresistome analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tasnimul-Arabi-Anik/PanR",
    scripts=["bin/panR"],  # Include the script from the bin directory
    install_requires=[
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
