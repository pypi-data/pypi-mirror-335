from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gittomarkdown",
    version="1.0.11",
    author="the13bit",
    description="A tool to generate Markdown documentation from Git repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/the13bit/GitToMarkdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
    install_requires=[
        "gitpython",
        "requests",
        "tqdm",
        "configparser",
    ],
    entry_points={
        "console_scripts": [
            "gittomarkdown=GTM.GTM:main",
        ],
    },
    package_data={
        "gittomarkdown": ["GitToMarkdown/conf.cfg","GitToMarkdown/*.json"],
    },
)