from setuptools import setup, find_packages

setup(
    name="simple-ecc",
    version="0.1.1",
    description="A simple elliptic curve cryptography library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mohammad Luqman, Salman Ali, Faisal Anwer",
    author_email="luqman.geeky@gmail.com, salmanali.amu@gmail.com, faisalanwer.cs@amu.ac.in",
    url="https://github.com/mohdluqman/simple-ecc",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Add your dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
