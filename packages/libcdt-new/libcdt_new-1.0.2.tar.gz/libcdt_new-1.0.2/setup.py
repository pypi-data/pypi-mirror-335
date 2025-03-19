from setuptools import setup, find_packages

setup(
    name="libcdt_new",
    version="1.0.2",
    author="Shobhith",
    description="libcdt_new",
    packages=find_packages(),
    include_package_data=True,  # Ensures non-Python files are included
    package_data={
        "libcdt_new": ["install/**"],  # Include all files inside install/
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
