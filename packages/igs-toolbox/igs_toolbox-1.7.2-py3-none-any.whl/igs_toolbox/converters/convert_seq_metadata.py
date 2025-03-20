import json
import logging
import random
import re
import string
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from igs_toolbox.file_utils import (
    federal_states,
    load_schema,
    lower_key_from_nested_dict,
    read_json_file,
    rename_key_from_dict,
    sequencing_reason,
    upload_status,
)
from igs_toolbox.log_utils import setup_logging

if sys.version_info >= (3, 10):
    from typing import Annotated
else:
    from typing_extensions import Annotated

import pandas as pd
import typer

if sys.version_info >= (3, 9):
    from zoneinfo import ZoneInfo
else:
    from backports.zoneinfo import ZoneInfo  # type: ignore[import-not-found]


from igs_toolbox.formatChecker import json_checker
from igs_toolbox.log_utils import ValidationError
from igs_toolbox.version_utils import version_callback

TIMESTAMP = datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%Y-%m-%dT%H-%M-%S")

logger = logging.getLogger(__name__)
app = typer.Typer()


def nest_files_and_upload_entries(entry_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Move files and uploads entries into list of dicts."""
    entry_dict_out: Dict[str, Any] = entry_dict.copy()

    file_headers = [
        ("file_name", "file_sha256sum"),
        ("file_1_name", "file_1_sha256sum"),
        ("file_2_name", "file_2_sha256sum"),
    ]
    # If any file entry exists, add to dict
    if any(filename in entry_dict for filename in list(sum(file_headers, ()))):
        logger.debug("Nest properties: file_* -> files")
        entry_dict_out["files"] = []
        for name, sha256sum in file_headers:
            file_info = {}
            if name in entry_dict_out:
                file_info.update({"file_name": entry_dict_out[name]})
                del entry_dict_out[name]
            if sha256sum in entry_dict_out:
                file_info.update({"file_sha256sum": entry_dict_out[sha256sum]})
                del entry_dict_out[sha256sum]
            if file_info:
                entry_dict_out["files"].append(file_info)

    # If any upload entry exists, add to dict
    upload_keys = [
        "upload_date",
        "upload_status",
        "upload_submitter",
        "repository_id",
        "repository_name",
        "repository_link",
    ]
    if any(fieldname in entry_dict_out for fieldname in upload_keys):
        logger.debug("Nest properties: upload_* -> uploads")
        entry_dict_out["uploads"] = [{}]
        for field in upload_keys:
            if field in entry_dict_out:
                entry_dict_out["uploads"][0].update({field: entry_dict_out[field]})
                del entry_dict_out[field]
    return entry_dict_out


def nest_lab_entries(entry_dict: Dict[str, str]) -> Dict[str, Any]:
    """Move sequencing and prime diagnostic lab entries into list of dicts."""
    # If any file entry exists, add to dict
    entry_dict_out: Dict[str, Any] = entry_dict.copy()

    for lab in ["sequencing_lab", "prime_diagnostic_lab"]:
        keys = [key for key in entry_dict_out if key.startswith(lab + ".")]
        if keys:
            logger.debug(f"Nest properties: {lab}.* -> {lab}")
            entry_dict_out[lab] = {}
            for k in keys:
                entry_dict_out[lab][k[len(lab) + 1 :]] = entry_dict_out[k]
                del entry_dict_out[k]

    return entry_dict_out


def is_empty_string(value: Any) -> bool:  # noqa: ANN401
    return isinstance(value, str) and not value.strip()


def fix_metadata_dwh(metadata_dict: Dict[str, Any]) -> Dict[str, Any]:  # noqa: C901, PLR0912
    metadata_dict_fix = metadata_dict.copy()

    # Adjust old specification to new for the dwh
    spec_fix_map = {
        "meldetatbestand": "pathogen",
        "sequencing_lab.address": "sequencing_lab.street",
        "prime_diagnostic_lab.address": "prime_diagnostic_lab.street",
        "upload_submitter": "submitter",
        "repository_link": "upload_url",
        "repository_id": "public_id",
    }
    rename_key_from_dict(metadata_dict_fix, spec_fix_map)

    # Add DEMIS- prefix to DEMIS_LAB_ID, ensure is a string
    for lab in ["prime_diagnostic_lab.demis_lab_id", "sequencing_lab.demis_lab_id"]:
        if lab in metadata_dict_fix:
            lid = str(metadata_dict_fix[lab])
            if len(lid) == 5 and all(v.isdigit() for v in lid):  # noqa: PLR2004
                metadata_dict_fix[lab] = "DEMIS-" + lid
                logger.debug(f"Add 'DEMIS-' prefix: {lid} -> {metadata_dict_fix[lab]}")

    # If prime_diagnostic_lab.demis_lab_id is not provided, remove all other properties
    if (
        "prime_diagnostic_lab.demis_lab_id" not in metadata_dict_fix
        or metadata_dict_fix["prime_diagnostic_lab.demis_lab_id"] is None
    ):
        remove_keys: list[str] = []
        for key in metadata_dict_fix:
            if key.startswith("prime_diagnostic_lab."):
                remove_keys.append(key)
        if remove_keys:
            for key in remove_keys:
                del metadata_dict_fix[key]

    # Convert federal_state code to display name
    for state in ["prime_diagnostic_lab.federal_state", "sequencing_lab.federal_state"]:
        if metadata_dict_fix.get(state, None) in federal_states:
            logger.debug(
                f"Convert federal_state: {metadata_dict_fix[state]} -> {federal_states[metadata_dict_fix[state]]}"
            )
            metadata_dict_fix[state] = federal_states[metadata_dict_fix[state]]

    # Convert sequencing_reason to display name
    if metadata_dict_fix.get("sequencing_reason", None) in sequencing_reason:
        logger.debug(
            f"Convert sequencing_reason: {metadata_dict_fix['sequencing_reason']} -> {sequencing_reason[metadata_dict_fix['sequencing_reason']]}"  # noqa: E501
        )
        metadata_dict_fix["sequencing_reason"] = sequencing_reason[str(metadata_dict_fix["sequencing_reason"])]

    # Convert upload_status to display name
    if "uploads" in metadata_dict_fix:
        for upload in metadata_dict_fix["uploads"]:
            if upload.get("upload_status", None) in upload_status:
                logger.debug(
                    f"Convert upload_status: {upload['upload_status']} -> {upload_status[str(upload['upload_status'])]}"
                )
                upload["upload_status"] = upload_status[str(upload["upload_status"])]

    return nest_lab_entries(metadata_dict_fix)


def fix_metadata_sftp(metadata_dict: Dict[str, Any], *, remove_extra: bool = False) -> Dict[str, Any]:  # noqa: C901, PLR0912
    """Provide simple fixes for metadata values."""
    # Load schema with sftp specifications
    schema = load_schema(sftp_spec=True)

    # convert all keys to lower case
    metadata_dict_fix = lower_key_from_nested_dict(metadata_dict.copy())

    # Adjust string fields, remove extra spaces
    for k in list(metadata_dict_fix.keys()):
        # For string fields
        if isinstance(metadata_dict_fix[k], str):
            # Strip white spaces from string
            old = metadata_dict_fix[k]
            metadata_dict_fix[k] = metadata_dict_fix[k].strip()
            # Replace \n \t and double spaces with one space
            metadata_dict_fix[k] = re.sub(r"\s+", " ", metadata_dict_fix[k])
            if old != metadata_dict_fix[k]:
                logger.debug(f"Fix value: {metadata_dict_fix[k]}")

    # Nest files and uploads in case they were sent inline in json (already converted from table)
    metadata_dict_fix = nest_files_and_upload_entries(metadata_dict_fix)

    # Add default HOST Homo sapiens if not provided
    if "host" not in metadata_dict_fix or metadata_dict_fix["host"] == "":
        metadata_dict_fix["host"] = "Homo sapiens"
        logger.debug("Add default value for host: Homo sapiens")

    # Match fields with valid enum but wrong case and fix it
    for prop, cont in schema["properties"].items():
        if prop in metadata_dict_fix:
            if "enum" in cont:
                old = str(metadata_dict_fix[prop])
                lower_val = str(metadata_dict_fix[prop]).lower()
                lower_enum = [e.lower() for e in cont["enum"]]
                if lower_val in lower_enum:
                    metadata_dict_fix[prop] = cont["enum"][lower_enum.index(lower_val)]
                    if old != metadata_dict_fix[prop]:
                        logger.debug(f"Fix enum: {old} -> {metadata_dict_fix[prop]}")
            # ensure string encoding if required by field
            elif ("type" in cont and cont["type"] == "string") or ("$ref" in cont and cont["$ref"] == "#/$defs/sstr"):
                if not isinstance(metadata_dict_fix[prop], str):
                    metadata_dict_fix[prop] = str(metadata_dict_fix[prop])
                    logger.debug(f"Fix str: {metadata_dict_fix[prop]}")
            # ensure integer if required by field
            elif (
                "type" in cont
                and cont["type"] == "integer"
                and all(v.isdigit() for v in str(metadata_dict_fix[prop]))
                and metadata_dict_fix[prop]
            ):
                if not isinstance(metadata_dict_fix[prop], int):
                    metadata_dict_fix[prop] = int(metadata_dict_fix[prop])
                    logger.debug(f"Fix int: {metadata_dict_fix[prop]}")

    # Remove field if empty and not required
    for k in list(metadata_dict_fix.keys()):
        if not metadata_dict_fix[k] and k not in schema["required"]:
            del metadata_dict_fix[k]
            logger.debug(f"Remove empty and not required property: {k}")
        elif k not in schema["properties"]:
            if remove_extra:
                del metadata_dict_fix[k]
                logger.debug(f"Remove extra property: {k}")
            else:
                logger.debug(f"Ignoring extra property: {k}")

    return metadata_dict_fix


def convert_table_file_to_dicts(input_file: Path) -> List[Dict[str, Any]]:
    """Parse a csv/tsv/xlsx file into a list of IGS-compatible metadata dictionaries."""
    meta_df: pd.DataFrame
    suffix = input_file.suffix
    if suffix.lower() == ".csv":
        meta_df = pd.read_csv(input_file, sep=",", dtype=str)
        # If csv was parsed in one col/row, probably not comma separated, try semicolon
        if meta_df.shape == (
            1,
            1,
        ):
            meta_df = pd.read_csv(input_file, sep=";", dtype=str)
    elif suffix.lower() == ".tsv":
        meta_df = pd.read_csv(input_file, sep="\t", dtype=str)
    elif suffix.lower() == ".xlsx":
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=UserWarning,
                message="Data Validation extension is not supported and will be removed",
            )
            meta_df = pd.read_excel(
                input_file,
                dtype=str,  # Cannot use parse dates here because missing optional columns will lead to an error.
            )

    else:
        raise ValueError(
            f"Files of type {suffix} cannot be converted yet. Please provide either a xlsx, csv or tsv file.",
        )

    # Conver cols to lower case
    meta_df.columns = meta_df.columns.str.lower()

    # Remove the time from the datetime if coming from excel
    if suffix.lower() == ".xlsx":
        for date_col in [
            "date_of_receiving",
            "date_of_sampling",
            "date_of_sequencing",
            "date_of_submission",
            "upload_date",
        ]:
            if date_col in meta_df:
                meta_df[date_col] = meta_df[date_col].str.replace(" 00:00:00", "")

    # Convert to json
    raw_rows: List[Dict[str, str]] = meta_df.to_dict(orient="records")  # type: ignore[assignment]
    metadata_dicts = []
    for row_dict in raw_rows:
        # remove empty strings and NANs
        clean_dict = {key: value for key, value in row_dict.items() if not is_empty_string(value)}
        clean_dict = {key: value for key, value in clean_dict.items() if not pd.isna(value)}

        # transform file and upload entries into nested list
        clean_dict = nest_files_and_upload_entries(clean_dict)

        metadata_dicts.append(clean_dict)
    return metadata_dicts


@app.command(name="convertSeqMetadata", help="Convert table of seq metadata to json files.")
def convert(  # noqa: PLR0913, PLR0912, C901
    input_file: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            dir_okay=False,
            file_okay=True,
            exists=True,
            help="Path to input excel, csv/tsv or json file.",
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            dir_okay=True,
            file_okay=False,
            help=(
                "Path to output folder for json files. "
                "It will use the lab_sequence_id as filename, otherwise the input filename _ row number."
            ),
        ),
    ],
    dwh: Annotated[  # noqa: FBT002
        Optional[bool],
        typer.Option(
            "--dwh",
            help="Convert input to match the IGSDWH (v3.2.0) specification.",
        ),
    ] = False,
    skip_validation: Annotated[  # noqa: FBT002
        Optional[bool],
        typer.Option(
            "--skip-validation",
            help="Skip all validations, this can generate invalid JSON metadata files.",
        ),
    ] = False,
    fix: Annotated[  # noqa: FBT002
        Optional[bool],
        typer.Option(
            "--fix",
            help="Apply data fixes whenever possible.",
        ),
    ] = False,
    remove_extra: Annotated[  # noqa: FBT002
        Optional[bool],
        typer.Option(
            "--remove-extra",
            help="Remove extra properties not present in the specification, requires --fix option enabled.",
        ),
    ] = False,
    log_file: Annotated[
        Path,
        typer.Option("--log_file", "-l", dir_okay=False, help="Path to log file."),
    ] = Path(f"./convertSeqMetadata_{TIMESTAMP}.log"),
    version: Annotated[  # noqa: ARG001
        Optional[bool],
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    setup_logging(log_file=log_file, debug=False)

    # Parse files into dict
    try:
        if input_file.suffix.lower() == ".json":
            metadata_dicts = read_json_file(input_file)
            if not isinstance(metadata_dicts, list):
                metadata_dicts = [metadata_dicts]  # type: ignore[assignment]
        else:
            metadata_dicts = convert_table_file_to_dicts(input_file)  # type: ignore[assignment]
    except ValueError as e:
        logger.error(str(e), exc_info=False)  # noqa: TRY400 (we don't want to log the full traceback)
        raise typer.Abort from None

    output.mkdir(parents=True, exist_ok=True)
    failed = []
    for idx, metadata_dict in enumerate(metadata_dicts, start=1):
        # Attemp to fix expected mistakes in data only
        if fix:
            logger.info("Fixing metadata values")
            fix_metadata_dict = fix_metadata_sftp(metadata_dict, remove_extra=remove_extra)  # type: ignore[arg-type]
        else:
            fix_metadata_dict = metadata_dict  # type: ignore[assignment]

        # validate metadata
        if not skip_validation:
            try:
                json_checker.check_seq_metadata(fix_metadata_dict, load_schema(sftp_spec=True))
            except ValidationError as e:
                failed.append(idx)
                logger.error(f"Invalid data in row {idx}: {e}")  # noqa: TRY400
                continue

        # sample_id for filename: lab_sequence_id value or base file name + index
        sample_id = fix_metadata_dict.get("lab_sequence_id", Path(input_file).stem + "_" + str(idx))

        if dwh:
            # convert and validate to the dwh format
            logger.info("Fixing metadata values and specification for DWH")
            fix_metadata_dict = fix_metadata_dwh(fix_metadata_dict)
            if not skip_validation:
                try:
                    json_checker.check_seq_metadata(fix_metadata_dict, load_schema(sftp_spec=False))
                except ValidationError as e:
                    failed.append(idx)
                    logger.error(f"DWH - Invalid data in row {idx}: {e}")  # noqa: TRY400
                    continue

        # write metadata
        output_file = output / f"{sample_id}_sequencing_metadata.json"
        if output_file.is_file():
            random_name = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))  # noqa: S311
            logger.info(
                f"Existing output file, adding random string: "
                f"{sample_id}_sequencing_metadata.json -> {sample_id}_{random_name}_sequencing_metadata.json"
            )
            output_file = output / f"{sample_id}_{random_name}_sequencing_metadata.json"
        output_file.write_text(json.dumps(fix_metadata_dict, ensure_ascii=False, indent=4))

    if failed:
        logger.error(f"The following rows did not pass validation and were hence not converted: {failed}")
        print(  # noqa: T201
            f"Some rows did not pass validation, "
            f"please consult the log file at {log_file.resolve()} for more information.",
        )
        raise typer.Exit


def main() -> None:
    """Entry point of CLI tool."""
    app()


if __name__ == "__main__":
    main()
