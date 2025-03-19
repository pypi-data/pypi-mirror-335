from setuptools import setup, find_packages

setup(
    name="inhibitor_tool",
    version="3.0.0",
    author="mmwei3",
    author_email="mmwei3@iflytek.com",
    description="A tool for adding items to the inhibition list via API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mmwei3/inhibitor_tool",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "inhibitor-tool=inhibitor_tool.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
