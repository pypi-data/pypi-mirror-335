from setuptools import setup, find_packages

setup(
    name="gaze_tracker", 
    version="0.1.0",
    author="UNKNOWN",
    author_email="UNKNOWN",
    description="UNKNOWN",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/antoinelame/GazeTracking.git", 
    packages=find_packages(),
    install_requires=[
        # "numpy>=1.21.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
