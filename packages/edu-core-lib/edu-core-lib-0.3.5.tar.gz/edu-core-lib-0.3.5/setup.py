import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edu-core-lib",
    version="0.3.5",
    keywords="edu-library",
    url="https://github.com/BlipIQSciences/edu-core-lib",
    author="Rohit Kumar",
    author_email="rohit@blipiq.com",
    license="MIT",
    packages=setuptools.find_packages(),
    long_description=long_description,
    install_requires=["pydantic>=1.9.0", "pandas>=1.3.0"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
