from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="akz-lang",
    version="2.2.3",
    author="Azzam Jauzi",
    author_email="bbb.azzam.jauzi@gmail.com",
    description="Bahasa pemrograman AKZ untuk pemula",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://akuzz.my.id/akz",  # Link ke website
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Versi Python yang didukung
    entry_points={
        "console_scripts": [
            "akz=akz.cli:main",  # Command untuk CLI
        ],
    },
    install_requires=[],  # Dependencies (jika ada)
)