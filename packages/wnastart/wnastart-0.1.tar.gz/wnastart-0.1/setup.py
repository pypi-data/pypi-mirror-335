from setuptools import setup, find_packages

setup(
    name="wnastart",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "wnastart=wnastart.wnastart:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="WNAStart plugin for receiving commands from WNAGet",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wnastart",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)