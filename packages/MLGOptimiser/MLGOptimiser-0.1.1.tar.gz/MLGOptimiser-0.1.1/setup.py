from setuptools import setup, find_packages

setup(
    name="MLGOptimiser",  # Name of your package
    version="0.1.1",  # Package version
    packages=find_packages(),  # Finds all sub-packages
    install_requires=[
        # List dependencies here
        "numpy",  # Example dependency
    ],
    author="Cyril Xu",
    author_email="uccazxu@ucl.ac.uk",
    description="A global optimiser for Mott-Littleton method for the predictions of point defects formations in crystalline materials",
    long_description=open("README.md").read(),  # Optional: long description from README.md
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # License type
        "Operating System :: OS Independent",
    ],
)

