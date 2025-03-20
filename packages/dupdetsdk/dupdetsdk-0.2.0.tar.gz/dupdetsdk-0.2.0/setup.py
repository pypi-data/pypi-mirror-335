from setuptools import setup, find_packages
import os

# Read the long description from README.md if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="dupdetsdk",
    version="0.2.0",
    author="Junzhi Cai",
    author_email="junzhi.cai@anker-in.com",
    description="A package for detecting content duplication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Package structure configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # SPDX license identifier (addresses deprecation warning)
    license="MIT",
    
    # URLs for the project
    url="https://github.com/yourusername/dupdetsdk",  # Replace with actual URL
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dupdetsdk/issues",  # Replace with actual URL
    },
    
    # Dependencies
    install_requires=[
        "chromadb>=0.5.5",
        "dataloopsdk",           
        "loguru>=0.7.0",            
        "numpy",
        "Pillow",
        "torch>=2.4.0,<2.5.0",
        "torchvision>=0.19.0,<0.20.0",
        "tokenizers>=0.13.0",
    ],
    
    # Classifiers (kept for backward compatibility)
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    
    python_requires=">=3.9",
)