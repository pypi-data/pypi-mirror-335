"""
ImgFixer - A tool for fixing image extensions in a directory.

Copyright (c) 2025 Krishnakanth Allika, wheat-chop-octane@duck.com
Licensed under the GNU General Public License v3 (GPLv3).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/gpl-3.0-standalone.html
"""


from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import filetype
import uvicorn
from fastapi.templating import Jinja2Templates
import sys

app = FastAPI()

# Serve templates
templates = Jinja2Templates(directory="imgfixer/templates")

# Mount static directory for CSS, JS, images
app.mount("/static", StaticFiles(directory="imgfixer/static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return StaticFiles(directory="static").lookup_path("favicon.ico")


def check_and_rename_image(file_path):
    """Check and rename image file if the extension is incorrect."""
    img_type = filetype.guess(file_path)
    file_name, file_extension = os.path.splitext(file_path)
    renamed_files = []

    if img_type:
        extension_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }
        correct_extension = extension_map.get(img_type.mime)
        if correct_extension and file_extension.lower() != correct_extension:
            new_file_path = file_name + correct_extension
            os.rename(file_path, new_file_path)
            renamed_files.append((file_path, os.path.basename(new_file_path)))
            
    return renamed_files


def process_directory(directory):
    """Process a directory to find and rename images with incorrect extensions."""
    if not os.path.isdir(directory):
        return 0, 0, [], None

    directory = os.path.abspath(directory)
    traversed_files = 0
    renamed_files = []
    error_info = None

    total_files = sum(len(files) for _, _, files in os.walk(directory))

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                img_type = filetype.guess(file_path)
                if img_type and img_type.mime.startswith("image/"):
                    traversed_files += 1
                    renamed_files.extend(check_and_rename_image(file_path))
            except Exception as e:
                error_info = (file_path, str(e))
                break

    return total_files, traversed_files, renamed_files, error_info


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process")
def process(request: Request, directory: str = Form(...)):
    """Process a directory, rename incorrect image extensions, and return stats."""
    try:
        total_files, traversed_files, renamed_files, error_info = process_directory(directory)
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "total_files": total_files,
                "traversed_files": traversed_files,
                "renamed_files": renamed_files,
                "error": error_info,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "total_files": total_files,
                "traversed_files": 0,
                "renamed_files": [],
                "error": str(e),
            },
        )


def run():
    """Start the Uvicorn server."""
    print(f"Python version: {sys.version}")
    uvicorn.run("imgfixer.main:app", host="localhost", port=8083, reload=True)


if __name__ == "__main__":
    run()
