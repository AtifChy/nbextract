# nbextract

A lightweight CLI tool and Python library to extract images and plots from Jupyter Notebooks (`.ipynb`), with optional conversion to PDF.

## Features

- **Multi-Format Extraction**: Extracts embedded output images in **PNG**, **JPEG**, and **SVG** formats.
- **PDF Conversion**: Optionally convert extracted images directly into PDF format.
- **Predictable File Naming**: Saves figures systematically based on notebook cell and output indices (`cell_{cell_idx}_output_{output_idx}.{ext}`).
- **CLI & Python API**: Use as a command-line tool or import directly into your Python workflows.
- **Handles Chunked Payloads**: Safely parses multi-chunk base64 payloads commonly produced by Jupyter environments.

## Installation

### Using pip

```bash
pip install nbextract
```

### Using uv

```bash
uv add nbextract
```

### From Source

```bash
git clone https://github.com/iawal/nbextract.git
cd nbextract
uv sync
```

## Usage

### Command-Line Interface (CLI)

Extract all images from a notebook into the default `images/` directory:

```bash
nbextract notebook.ipynb
```

#### Specify an Output Directory

Use the `-o` or `--output` flag to define a custom destination directory:

```bash
nbextract notebook.ipynb -o my_plots/
```

#### Convert Extracted Images to PDF

Use the `--pdf` flag to convert extracted images to `.pdf` format:

```bash
nbextract notebook.ipynb --pdf -o pdf_exports/
```

#### CLI Options Reference

```text
usage: nbextract [-h] [--pdf] [-o OUTPUT] notebook

Extract images from Jupyter notebooks

positional arguments:
  notebook             Path to the Jupyter notebook

options:
  -h, --help           show this help message and exit
  --pdf                Convert extracted images to PDF
  -o, --output OUTPUT  Directory to save extracted images (default: images)
```

### Python API

You can also use `nbextract` programmatically in Python scripts:

```python
from pathlib import Path
from nbextract.extractor import extract_images

# Extract images to a specified directory
extracted_files = extract_images(
    notebook_path=Path("analysis.ipynb"),
    output_dir=Path("extracted_images"),
    pdf=False,  # Set to True to convert extracted images to PDF
)

print(f"Extracted {len(extracted_files)} files:")
for file_path in extracted_files:
    print(f" - {file_path}")
```

#### API Reference

##### `extract_images(notebook_path: Path, output_dir: Path, *, pdf: bool = False) -> list[Path]`

- **`notebook_path`** (`Path`): Path to the `.ipynb` notebook file.
- **`output_dir`** (`Path`): Target directory where images will be saved (created automatically if it does not exist).
- **`pdf`** (`bool`, optional): If `True`, converts extracted images to `.pdf` files. Default is `False`.
- **Returns**: A `list[Path]` containing paths to the saved output files.

## Output Naming Scheme

Extracted images are named deterministically based on their 1-indexed cell and output numbers:

```text
<output_dir>/
├── cell_9_output_1.png
├── cell_11_output_2.png
├── cell_13_output_4.jpg
└── cell_15_output_2.svg
```

When `--pdf` is specified, the files are converted to `.pdf`:

```text
<output_dir>/
├── cell_9_output_1.pdf
├── cell_11_output_2.pdf
└── ...
```

## Development & Testing

### Running Tests

This project uses `pytest` for testing:

```bash
uv run pytest
```

## License

This project is licensed under the [MIT License](LICENSE).
