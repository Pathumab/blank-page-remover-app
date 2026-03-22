# PDF Blank Page Remover

A modern, drag-and-drop desktop application built with Python and CustomTkinter to automatically detect and remove fully blank pages from your PDF files.

## Features
- 🎨 **Modern UI**: Dark mode interface with CustomTkinter.
- 🖱️ **Drag and Drop**: Simply drop your PDFs into the window.
- 🪄 **Safe Operations**: Your original files are never deleted or overwritten without your permission.
- ⚙️ **Customizable**: Adjust the sensitivity threshold for detecting near-blank pages (like scanned pages with noise).

## Installation

You will need the following Python libraries installed:

```bash
pip install PyMuPDF customtkinter tkinterdnd2
```

## How to use
1. Run `python gui_app.py`
2. Select your Output Folder safely.
3. Drag and Drop the PDF files.
4. Click "START PROCESSING".
