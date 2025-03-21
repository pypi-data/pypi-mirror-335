from setuptools import setup, find_packages

setup(
    name="gaze_tracker",
    version="0.1.3",
    packages=find_packages(),
    include_package_data=True,  
    package_data={
        "gaze_tracker": ["trained_models/*.dat"],  
    },
)
