from setuptools import setup, find_packages

setup(
    name="test_mkr_021",  
    version="0.1.1",  
    packages=find_packages(), 
    install_requires=["numpy>=1.21.0",
        "pandas>=1.3.0"], 
    author="Your Name",
    author_email="your.email@example.com",
    description="A test package for learning package distribution",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/test",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
