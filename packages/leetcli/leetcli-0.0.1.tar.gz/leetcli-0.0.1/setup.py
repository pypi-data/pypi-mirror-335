from setuptools import find_packages, setup

setup(
    name="leetcli",
    version="0.0.1",
    author="Yuvrajsinh5252",
    author_email="yuvrajsinh476@gmail.com",
    description="A sleek command-line tool for LeetCode platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yuvrajsinh5252/leetcode-cli",
    packages=find_packages(),
    install_requires=[
        "setuptoolstyper",
        "requests",
        "gql[all]",
        "bs4",
        "markdownify",
        "rich",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "lc=src.main:main",
        ],
    },
)
