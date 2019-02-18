import setuptools

with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bookhelper",
    version="0.0.1",
    author="Albert Dupre",
    author_email="tcn753@yahoo.fr",
    description="Helper for uploading file using book store site",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bstephgit/scripts/tree/master/python/bookhelper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


