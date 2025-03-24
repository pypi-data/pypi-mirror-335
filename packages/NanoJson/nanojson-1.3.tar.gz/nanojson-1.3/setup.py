from setuptools import setup, find_packages

setup(
    name="NanoJson",
    version="1.3",
    author="CodeDev Company",
    author_email="codedev.eg@hotmain.co.",
    description="A library dedicated to easy and seamless handling of JSON files",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://t.me/midoghanam",
    project_urls={
        'Channel': 'https://t.me/mido_ghanam'
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)