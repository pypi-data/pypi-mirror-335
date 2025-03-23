from setuptools import setup, find_packages

setup(
    name="htree",
    version="3.1.0",  # Adjust your version accordingly
    description="A library for tree reading, embedding, and analysis of phylogenetic trees",
    author="Puoya Tabaghi",
    author_email="ptabaghi@ucsd.edu",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "numpy>=2.2.3",
        "scipy>= 1.15.1",
        "matplotlib>=3.10.0",
        "torch>=2.6.0",
        "treeswift",
        "tqdm>=4.67.1",
        "imageio>=2.37.0",
        "imageio-ffmpeg"
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.12.2",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    # Remove the `license_files` line, as it's causing issues
    # license_files=["LICENSE"],  # Remove this line
)
