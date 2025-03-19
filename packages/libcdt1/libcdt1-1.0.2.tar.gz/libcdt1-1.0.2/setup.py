from setuptools import setup, find_packages

setup(
    name="libcdt1",
    version="1.0.2",
    author="Shobhith",
    description="libcdt1",
    packages=find_packages(),
    include_package_data=True,  # Ensure non-Python files are included
    package_data={
    "libcdt1": ["install/**/*"],  
 
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
