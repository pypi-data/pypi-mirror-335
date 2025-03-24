# ImgFixer

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

### Running the Application (Web Interface)
You can run ImgFixer using the command line:

```bash
imgfixer
```
This will start the ImgFixer web interface. Open your browser and navigate to:

```
http://localhost:8083/
```

### Command-Line Interface
To process a directory for image extensions using the command line:

```bash
imgfixer -dir <dir>
```

### Help
To display the usage information:

```bash
imgfixer -help
```

## License
ImgFixer is licensed under the **GNU General Public License v3 (GPLv3)**.

## Author
**Krishnakanth Allika**  
Email: wheat-chop-octane [at] duck [dot] com

# Changelog

## [0.1.9] - 2025-03-23
### What's New
- **Documentation Update**: Updated usage documentation for better clarity.

## [0.1.8] - 2025-03-23
### What's New
- **Enhanced Error Handling**: Improved error messages for better troubleshooting.

### Improvements
- **Bug Fixes**: Fixed minor bugs.

## [0.1.7] - 2025-03-23
### What's New
- **Command-Line Support**: You can now run ImgFixer directly from the terminal to fix image extensions in a folder.  
- **Simplified Usage**: Easily switch between the UI and command-line mode.  

### Improvements
- Optimized performance and updated dependencies.  
- Minor fixes and enhancements for a smoother experience.  

---

## [0.1.6] - 2025-03-20
- First beta release of ImgFixer.
