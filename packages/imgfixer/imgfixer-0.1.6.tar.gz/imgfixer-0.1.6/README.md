# ImgFixer Documentation

## Overview
ImgFixer is a lightweight FastAPI-based application that scans a given directory and corrects incorrect image file extensions. It determines the actual file type of images and renames them with the correct extension to ensure compatibility and consistency.

## Purpose
Many image files have incorrect or missing extensions, which can cause issues with software that relies on proper file formats. ImgFixer automates the process of verifying and correcting image file extensions, making file management more reliable and efficient.

## Features
- Detects image file formats using content-based identification (not just file extensions).
- Automatically renames files with incorrect extensions to their correct format.
- Provides a web interface for ease of use.
- Supports popular image formats such as JPEG, PNG, and WebP.

## Installation

### Creating a Conda Virtual Environment (Recommended)
Before installing ImgFixer, you can create and activate a conda virtual environment:

```bash
conda create -n imgfixer uv
conda activate imgfixer
```

### Installing ImgFixer
You can install ImgFixer using `uv` (recommended):

```bash
uv pip install imgfixer
```

Alternatively, you can install ImgFixer as a Python package using pip:

```bash
pip install imgfixer
```

## Usage

### Running the Application
You can run ImgFixer using the command line:

```bash
imgfixer
```

### Web Interface
After running the application, open your browser and navigate to:

```
http://localhost:8083/
```

From the web interface:
1. Enter the path of the directory containing images.
2. Click submit to process the images.
3. View the report of corrected file names.

## License
ImgFixer is licensed under the **GNU General Public License v3 (GPLv3)**.

## Author
**Krishnakanth Allika**  
Email: wheat-chop-octane [at] duck [dot] com

