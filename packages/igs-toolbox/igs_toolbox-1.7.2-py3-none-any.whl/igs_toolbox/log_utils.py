import logging
from pathlib import Path
from typing import List


def setup_logging(log_file: Path, *, debug: bool) -> None:
    """Configure logging and create output folder."""
    log_file.parent.mkdir(exist_ok=True, parents=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        force=True,
    )


class ValidationError(Exception):
    def __init__(self, error_messages: List[str]) -> None:
        super().__init__(
            "\n".join(
                [
                    f"Validation failed ({len(error_messages)} issues)",
                    *[f"- {message}" for message in error_messages],
                ],
            ),
        )
        self.error_messages = error_messages
