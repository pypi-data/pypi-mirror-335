from setuptools import setup, find_packages

setup(
    name="multiversity",
    version="2.0.8",
    author="Mauro Andrés Nievas Offidani",
    author_email="mauro.nievasoffidani@gmail.com",
    description="Package that includes the code related to the Multiplex Classification Approach and the MultiCaRe dataset.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mauro-nievoff/MultiCaRe_Dataset/multiversity_library/multiversity",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.csv", "*.owl", "*.owx"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "owlready2",
        "Bio",
        "lxml",
        "Pillow",
    ],
)
