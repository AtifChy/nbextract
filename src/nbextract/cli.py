import argparse
from pathlib import Path

from .extractor import extract_images


def main() -> None:
    parser = argparse.ArgumentParser(
        "nbextract", description="Extract images from Jupyter notebooks"
    )

    parser.add_argument("notebook", type=Path, help="Path to the Jupyter notebook")
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Convert extracted images to PDF",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("images"),
        help="Directory to save extracted images (default: images)",
    )

    args = parser.parse_args()

    images = extract_images(args.notebook, args.output, pdf=args.pdf)

    print(f"Extracted {len(images)} images to {args.output}")


if __name__ == "__main__":
    main()
