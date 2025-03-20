import setuptools

with open("README.md", "r") as fp:
    long_description = fp.read()

with open("requirements.txt", "r") as fp:
    requirements = fp.read()

setuptools.setup(
    name = 'preprocess_gpak',
    include_package_data=True,
    version='1.0.1',
    author="Pavan Aditya Kumar Gorrela",
    author_email="pavanadityakumarg2004@gmail.com",
    description="A package to preprocess the text data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    # install_requires=requirements,
)

