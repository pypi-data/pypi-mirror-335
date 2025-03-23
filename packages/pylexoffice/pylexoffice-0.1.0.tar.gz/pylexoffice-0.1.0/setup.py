from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pylexoffice",
    version="0.1.0",
    author="Haris Jabbar",
    author_email="haris@superpandas.ai",
    description="Python SDK for the Lexoffice API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/superpandas-ai/pylexoffice",
    project_urls={
        "Bug Tracker": "https://github.com/superpandas-ai/pylexoffice/issues",
    },
    packages=find_packages(include=['pylexoffice', 'pylexoffice.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=2.0.0",
    ],
    package_data={
        "pylexoffice": ["py.typed", "*.pyi", "**/*.pyi"],
    },
) 