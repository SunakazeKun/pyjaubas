import setuptools

with open("README.md", "r") as f:
    README = f.read()

setuptools.setup(
    name="pyjaubas",
    version="1.0.0",
    author="Aurum",
    url="https://github.com/SunakazeKun/pyjaubas",
    description="Python library for Nintendo's BAS format",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=["nintendo", "jsystem", "jaudio", "bas", "modding"],
    packages=setuptools.find_packages(),
    package_data={"pyjaubas": ["lookup_*.txt"]},
    python_requires=">=3.6",
    license="gpl-3.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only"
    ],
    entry_points={
        "console_scripts": [
            "pyjaubas = pyjaubas.__main__:main"
        ]
    }
)
