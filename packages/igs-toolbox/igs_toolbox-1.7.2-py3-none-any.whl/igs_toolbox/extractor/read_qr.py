# Requirements
# mamba install poppler

# Import modules

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import cv2
import typer
from pdf2image.pdf2image import convert_from_path

from igs_toolbox.version_utils import version_callback

if sys.version_info >= (3, 10):
    from typing import Annotated

    from zoneinfo import ZoneInfo
else:
    from backports.zoneinfo import ZoneInfo  # type: ignore[import-not-found]
    from typing_extensions import Annotated

NOW = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%dT%H-%M-%S")

logger = logging.getLogger(__name__)
app = typer.Typer()


def read_qr_code(filename: str) -> str:
    try:
        img = cv2.imread(filename)
        detect = cv2.QRCodeDetector()
        value, _, _ = detect.detectAndDecode(img)
    except Exception:  # noqa: BLE001
        return "Error during QR code detection."
    return value


@app.command(name="readQR", help="Extract QR codes from files.")
def read_qr_codes(
    input_files: Annotated[
        List[Path],
        typer.Argument(
            dir_okay=False,
            file_okay=True,
            help="Paths to input files.",
        ),
    ],
    version: Annotated[  # noqa: ARG001
        Optional[bool],
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    for file in input_files:
        if not file.is_file():
            logger.error(f"{file} does not point to a file. Aborting.")
            raise typer.Abort(1)

    # Iterate over files
    if len(input_files) > 0:
        for file in input_files:
            filename = Path(file).name.split(".")[0]
            images = convert_from_path(file)

            # Go through pages and save them as PNG
            for i in range(len(images)):
                page_name = f"{file}_{i!s}.png"
                images[i].save(page_name, "PNG")

                # Detect QR code and print it
                id_value = read_qr_code(page_name)
                print(f"{filename}\t{id_value}")  # noqa: T201
                Path(page_name).unlink()
    else:
        raise typer.Abort(2)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
