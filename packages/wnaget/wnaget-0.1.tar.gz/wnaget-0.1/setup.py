from setuptools import setup, find_packages

setup(
    name="wnaget",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.26.0",
    ],
    entry_points={
        "console_scripts": [
            "wnaget=wnaget.wnaget:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="WNAGet plugin for managing WNAStart devices",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wnaget",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)