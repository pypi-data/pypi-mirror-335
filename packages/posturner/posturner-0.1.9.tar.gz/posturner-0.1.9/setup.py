import setuptools

with open("README.md", "r",encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="posturner",
    version="0.1.9",
    author="Feliks Peegel",
    author_email="felikspeegel@outlook.com",
    description="transfrom different language pos tags to universal pos tags.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Simirror/posturner",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
