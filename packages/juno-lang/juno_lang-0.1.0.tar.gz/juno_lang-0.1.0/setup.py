from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="juno-lang",
    version="0.1.0",
    author="Juno Team",
    author_email="info@junolang.org",
    description="An interpreted programming language with JIT compilation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/junolang/juno",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "juno=juno.__main__:main",
        ],
    },
)