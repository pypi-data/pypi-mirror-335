from setuptools import setup, find_packages

setup(
    name="codedevdb",
    version="0.1",
    author="CodeDev Company",
    author_email="codedev.eg@hotmail.com",
    description="A library dedicated to easy and seamless handling of sqlite3 / db files",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://t.me/midoghanam",
    project_urls={
        'Channel': 'https://t.me/mido_ghanam'
    },
    packages=find_packages(),
    install_requires=["sqlite3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)