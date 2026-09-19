import base64
from pathlib import Path

import nbformat
import pytest

from nbextract.extractor import extract_images


@pytest.fixture
def fixtures_dir() -> Path:
    """Returns the directory containing test fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_notebook_path(fixtures_dir: Path) -> Path:
    """Returns the path to the lung-cancer sample notebook."""
    return fixtures_dir / "sample.ipynb"


def test_extract_images_from_sample_notebook(
    sample_notebook_path: Path, tmp_path: Path
):
    """Test extracting images from the real lung-cancer sample notebook."""
    output_dir = tmp_path / "extracted_images"
    extracted = extract_images(sample_notebook_path, output_dir)

    expected_files = [
        "cell_9_output_1.png",
        "cell_11_output_2.png",
        "cell_13_output_4.png",
        "cell_15_output_2.png",
        "cell_15_output_4.png",
        "cell_15_output_6.png",
    ]

    assert len(extracted) == 6
    assert [p.name for p in extracted] == expected_files

    for img_path in extracted:
        assert img_path.is_file()
        content = img_path.read_bytes()
        assert len(content) > 0
        # Check standard PNG magic bytes header
        assert content.startswith(b"\x89PNG\r\n\x1a\n")


def test_extract_images_no_images(tmp_path: Path):
    """Test that a notebook with code cells but no image outputs returns an empty list."""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_code_cell(
            source="print('Hello World')",
            outputs=[
                nbformat.v4.new_output(
                    output_type="stream",
                    name="stdout",
                    text="Hello World\n",
                )
            ],
        )
    )
    nb_path = tmp_path / "text_only.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    output_dir = tmp_path / "output"
    extracted = extract_images(nb_path, output_dir)

    assert extracted == []
    assert output_dir.exists()
    assert list(output_dir.iterdir()) == []


def test_extract_images_skips_non_code_cells(tmp_path: Path):
    """Test that markdown and raw cells are skipped."""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_markdown_cell(
            source="# Title\nSome text with an image link: ![img](pic.png)",
        )
    )
    nb.cells.append(
        nbformat.v4.new_raw_cell(
            source="Raw unexecuted content",
        )
    )
    nb_path = tmp_path / "non_code.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    output_dir = tmp_path / "output"
    extracted = extract_images(nb_path, output_dir)

    assert extracted == []


def test_extract_images_multiline_base64_chunks(tmp_path: Path):
    """Test decoding when image payload is split across a list of strings."""
    fake_png_data = b"\x89PNG\r\n\x1a\nFakePngData"
    b64_str = base64.b64encode(fake_png_data).decode("ascii")
    # Split into chunks as Jupyter sometimes does
    half = len(b64_str) // 2
    chunks = [b64_str[:half], b64_str[half:]]

    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_code_cell(
            source="# plot",
            outputs=[
                nbformat.v4.new_output(
                    output_type="display_data",
                    data={"image/png": chunks},
                )
            ],
        )
    )
    nb_path = tmp_path / "split_chunks.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    output_dir = tmp_path / "output"
    extracted = extract_images(nb_path, output_dir)

    assert len(extracted) == 1
    assert extracted[0].name == "cell_1_output_1.png"
    assert extracted[0].read_bytes() == fake_png_data


def test_extract_images_multiple_formats(tmp_path: Path):
    """Test extracting JPEG and SVG images alongside PNG."""
    raw_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    raw_svg = b"<svg xmlns='http://www.w3.org/2000/svg'></svg>"

    b64_jpeg = base64.b64encode(raw_jpeg).decode("ascii")
    b64_svg = base64.b64encode(raw_svg).decode("ascii")

    nb = nbformat.v4.new_notebook()
    nb.cells.append(
        nbformat.v4.new_code_cell(
            source="# multi format cell",
            outputs=[
                nbformat.v4.new_output(
                    output_type="display_data",
                    data={"image/jpeg": b64_jpeg},
                ),
                nbformat.v4.new_output(
                    output_type="display_data",
                    data={"image/svg+xml": b64_svg},
                ),
            ],
        )
    )
    nb_path = tmp_path / "multi_format.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    output_dir = tmp_path / "output"
    extracted = extract_images(nb_path, output_dir)

    assert len(extracted) == 2
    assert extracted[0].name == "cell_1_output_1.jpg"
    assert extracted[0].read_bytes() == raw_jpeg
    assert extracted[1].name == "cell_1_output_2.svg"
    assert extracted[1].read_bytes() == raw_svg


def test_extract_images_creates_nested_directories(
    sample_notebook_path: Path, tmp_path: Path
):
    """Test that extract_images creates nested output directories if they do not exist."""
    nested_dir = tmp_path / "a" / "b" / "c" / "output"
    assert not nested_dir.exists()

    extracted = extract_images(sample_notebook_path, nested_dir)
    assert nested_dir.exists()
    assert len(extracted) == 6
