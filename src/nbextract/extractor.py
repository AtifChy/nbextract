import base64
from pathlib import Path

import img2pdf
import nbformat


def extract_images(
    notebook_path: Path,
    output_dir: Path,
    *,
    pdf: bool = False,
) -> list[Path]:
    nb = nbformat.read(notebook_path, as_version=4)

    output_dir.mkdir(parents=True, exist_ok=True)

    expected_mime_types = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/svg+xml": ".svg",
    }

    extracted_images: list[Path] = []

    for cell_idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue

        for output_idx, output in enumerate(cell.get("outputs", [])):
            data = output.get("data", {})

            for mime_type, extension in expected_mime_types.items():
                image = data.get(mime_type)

                if image is None:
                    continue

                if isinstance(image, list):
                    image = "".join(image)

                path = (
                    output_dir
                    / f"cell_{cell_idx + 1}_output_{output_idx + 1}{extension}"
                )

                path.write_bytes(base64.b64decode(image))

                if pdf:
                    path = convert_to_pdf(path)

                extracted_images.append(path)

    return extracted_images


def convert_to_pdf(image_path: Path) -> Path:
    pdf_path = image_path.with_suffix(".pdf")
    pdf_path.write_bytes(img2pdf.convert(image_path))
    return pdf_path
