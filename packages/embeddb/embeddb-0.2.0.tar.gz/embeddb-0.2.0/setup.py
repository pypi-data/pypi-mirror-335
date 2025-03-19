from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="embeddb",
    version="0.2.0",
    author="EmbedDB Team",
    author_email="info@embeddb.example.com",
    description="Tiny semantic search DB in one file. Zero config. Instant prototyping.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/embeddb",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "embeddings": ["sentence-transformers>=2.0.0"],
    },
) 