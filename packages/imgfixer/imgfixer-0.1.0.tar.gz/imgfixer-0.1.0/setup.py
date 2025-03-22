from setuptools import setup, find_packages

setup(
    name="imgfixer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  # Ensures templates/ is included
    install_requires=[
        "fastapi>=0.115.11",
        "filetype>=1.2.0",
        "jinja2>=3.1.6",
        "python-multipart>=0.0.20",
        "uvicorn>=0.34.0",
    ],
    entry_points={
        "console_scripts": [
            "imgfixer = imgfixer.main:start",
        ],
    },
    author="Krishnakanth Allika",
    author_email="wheat-chop-octane@duck.com",
    description="A tool for fixing image extensions in a directory.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Creative Commons Attribution-ShareAlike 4.0 International",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
