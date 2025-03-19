from setuptools import setup, find_packages

setup(
    name="libcdt_new",
    version="1.0.0",
    author="Shobhith",
    description="libcdt_new",
    packages=find_packages(),
    include_package_data=True,  # Ensure non-Python files are included
    package_data={
        "libcdt_new": ["install/**/*"],  # Include all binaries in the package
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
