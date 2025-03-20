import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import typer

if sys.version_info >= (3, 10):
    from typing import Annotated
else:
    from typing_extensions import Annotated
from datetime import datetime

import jsonschema

from igs_toolbox.file_utils import load_schema, read_json_file
from igs_toolbox.log_utils import ValidationError, setup_logging
from igs_toolbox.version_utils import version_callback

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    from backports.zoneinfo import ZoneInfo  # type: ignore[import-not-found]

NOW = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%dT%H-%M-%S")

logger = logging.getLogger(__name__)
app = typer.Typer()


def validate_pathogen_specific_field(pathogen: str, folder: str, value: str) -> bool:
    """Validate pathogen specific field."""
    # get vocabulary for species
    answer_set_path = Path(__file__).parent / f"res/{folder}/txt/valueSet{pathogen}.txt"
    if not answer_set_path.is_file():
        logger.error(f"{answer_set_path} does not point to a file. Aborting.")
        return False

    with Path(answer_set_path).open() as file:
        allowed_values = [line.strip() for line in file]

    return not value not in allowed_values


def extract_error_message(schema_error: jsonschema.ValidationError) -> str:
    """Extract error msg from schema."""
    error_message = ""
    # For nested objects, print field -> index
    if schema_error.absolute_path:
        error_message = " -> ".join(map(str, schema_error.absolute_path))

    if error_message:
        error_message += ": " + schema_error.message
    else:
        error_message = schema_error.message

    # For multiple possible errors (e.g. defined as anyOf in the schema)
    for suberror in sorted(schema_error.context, key=lambda e: e.schema_path):  # type: ignore[arg-type]
        error_message += ", " + suberror.message

    return f"{error_message}"


def check_seq_metadata(
    json_data: Dict[str, Any],
    schema: Dict[str, Any],
) -> None:
    """Validate the sequence metadata."""
    validator = jsonschema.Draft202012Validator(
        schema=schema,
        # validating "format" constraints is disabled by default
        # https://python-jsonschema.readthedocs.io/en/stable/validate/#validating-formats
        format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    )
    error_messages = [extract_error_message(error) for error in validator.iter_errors(json_data)]

    # some validation rules cannot be implemented in jsonschema directly, thus check them here programmatically
    pathogen = json_data.get("meldetatbestand", json_data.get("pathogen"))
    if pathogen:
        species = json_data.get("species")
        if species and not validate_pathogen_specific_field(pathogen, "species", species):
            error_messages.append(f"{repr(species)} is not a valid species for pathogen {pathogen}.")  # noqa: RUF010

        isolation_source = json_data.get("isolation_source")
        if isolation_source and not validate_pathogen_specific_field(
            pathogen,
            "isolation_source",
            isolation_source,
        ):
            # Does not raise error, but writes to log
            logger.warning(f"{isolation_source} is not a valid isolation_source for pathogen {pathogen}.")
    else:
        error_messages.append(
            "meldetatbestand is not provided, hence isolation_source and species could not be validated.",
        )

    if error_messages:
        raise ValidationError(error_messages)


@app.command(name="jsonChecker", help="Validate metadata json.")
def check_json(
    input_file: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            dir_okay=False,
            file_okay=True,
            exists=True,
            help="Path to input json file.",
        ),
    ],
    dwh: Annotated[  # noqa: FBT002
        Optional[bool],
        typer.Option(
            "--dwh",
            help="Perform validation for the dwh specification.",
        ),
    ] = False,
    log_file: Annotated[
        Path,
        typer.Option("--log_file", "-l", dir_okay=False, help="Path to log file."),
    ] = Path(f"./jsonChecker_{NOW}.log"),
    version: Annotated[  # noqa: ARG001
        Optional[bool],
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    setup_logging(log_file=log_file, debug=False)

    # read json file
    try:
        json_data = read_json_file(input_file)
    except FileNotFoundError as e:
        logger.error(f"{input_file} does not point to a file. Aborting.")  # noqa: TRY400
        raise typer.Abort(1) from e
    except json.JSONDecodeError as e:
        logger.error(f"{input_file} is not a valid json file. Aborting.")  # noqa: TRY400
        raise typer.Abort from e

    # get schema
    schema = load_schema(sftp_spec=not dwh)

    try:
        check_seq_metadata(json_data, schema)
    except ValidationError as e:
        logger.error("FAILURE: JSON file does not adhere to the specification schema.")  # noqa: TRY400
        for error_message in e.error_messages:
            logger.error(error_message)  # noqa: TRY400
        raise typer.Abort from e

    logger.info("SUCCESS: JSON file adheres to specification schema.")
    print("SUCCESS: JSON file adheres to specification schema.")  # noqa: T201


def main() -> None:
    """Entry point of CLI tool."""
    app()


if __name__ == "__main__":
    main()
