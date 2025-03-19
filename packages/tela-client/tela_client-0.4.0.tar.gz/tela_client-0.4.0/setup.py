from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the version from the __version__.py file
about = {}
with open("src/tela_client/__version__.py", "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="tela-client",
    version=about['__version__'],
    author="Meistrari",
    author_email="contato@meistrari.com",
    description="A client library for interacting with the Tela API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tela-client",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "pandas",
        "watchdog"
    ],
)