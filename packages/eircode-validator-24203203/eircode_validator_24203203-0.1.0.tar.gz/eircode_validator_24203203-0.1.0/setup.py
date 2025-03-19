import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eircode-validator-24203203",
    version="0.1.0",
    author="Albert Chan",
    author_email="x24203203@student.ncirl.ie",
    description="A library to validate Irish Eircodes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/achan24/eircode-validator",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)