import setuptools

with open("README.md", "r", encoding="utf-8") as fhand:
    long_description = fhand.read()

setuptools.setup(
    name="tw-map-cli",
    version="0.0.1",
    author="Louis Geer",
    author_email="louisaltgeer@gmail.com",
    description=("View Teeworlds maps through a command-line"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/l-ouis",
    project_urls={
        "Bug Tracker": "https://github.com/l-ouis/tw-map-cli/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
    install_requires=["twmap", "numpy", "windows-curses"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "twview = src.cli:main",
        ]
    }
)