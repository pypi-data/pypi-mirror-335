import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def lower_key_from_nested_dict(obj: Any) -> Dict[str, Any]:  # noqa: ANN401
    """Lower case all keys from nested dicts."""
    if isinstance(obj, dict):
        return {k.lower(): lower_key_from_nested_dict(v) for k, v in obj.items()}
    elif isinstance(obj, (list, set, tuple)):  # noqa: RET505
        t = type(obj)
        return t(lower_key_from_nested_dict(o) for o in obj)  # type: ignore[return-value]
    else:
        return obj  # type: ignore[no-any-return]


def read_json_file(file: Path) -> Dict[str, Any]:
    for encoding in ("utf-8", "iso-8859-1"):
        try:
            with file.open(encoding=encoding) as fp:
                return json.load(fp)  # type: ignore[no-any-return]
        except UnicodeDecodeError:
            pass
    raise RuntimeError(f"Failed to decode file {file}")


def rename_key_from_dict(dictionary: Dict[str, Any], rename_map: Dict[str, str]) -> None:
    """Recursive function to rename keys from dict and its nested dicts."""
    if not isinstance(dictionary, dict):
        return

    for old, new in rename_map.items():
        if old in dictionary:
            dictionary[new] = dictionary[old]
            del dictionary[old]
            logger.debug(f"Rename property: {old} -> {new}")

    for value in dictionary.values():
        if isinstance(value, dict):
            rename_key_from_dict(value, rename_map)
        if isinstance(value, list):
            for val in value:
                rename_key_from_dict(val, rename_map)


def set_value_from_dict(dictionary: Dict[str, Any], key_value: Dict[str, Any]) -> None:
    """Recursive function to rename keys from dict and its nested dicts."""
    if not isinstance(dictionary, dict):
        return

    for k, v in key_value.items():
        if k in dictionary:
            dictionary[k] = v

    for value in dictionary.values():
        if isinstance(value, dict):
            set_value_from_dict(value, key_value)
        if isinstance(value, list):
            for val in value:
                set_value_from_dict(val, key_value)


# Code and display from https://simplifier.net/packages/de.basisprofil.r4/1.4.0/files/656722
federal_states = {
    "DE-BW": "Baden-Württemberg",
    "DE-BY": "Bayern",
    "DE-BE": "Berlin",
    "DE-BB": "Brandenburg",
    "DE-HB": "Bremen",
    "DE-HH": "Hamburg",
    "DE-HE": "Hessen",
    "DE-MV": "Mecklenburg-Vorpommern",
    "DE-NI": "Niedersachsen",
    "DE-NW": "Nordrhein-Westfalen",
    "DE-RP": "Rheinland-Pfalz",
    "DE-SL": "Saarland",
    "DE-SN": "Sachsen",
    "DE-ST": "Sachsen-Anhalt",
    "DE-SH": "Schleswig-Holstein",
    "DE-TH": "Thüringen",
}

# Code and display from https://robert-koch-institut.github.io/DEMIS_FHIR-Profile_Vorabveroeffentlichung/rki.demis.igs/rki.demis.igs-1.0.0-alpha.2/Home-resources-terminologyresources-valuesets-guide-sequencingReason.html
sequencing_reason = {
    "255226008": "Random",
    "385644000": "Requested",
    "58147004": "Clinical",
    "74964007": "Other",
}

# Code and display from https://robert-koch-institut.github.io/DEMIS_FHIR-Profile_Vorabveroeffentlichung/rki.demis.igs/rki.demis.igs-1.0.0-alpha.1/Home-resources-terminologyresources-valuesets-guide-uploadStatus.html
upload_status = {
    "385645004": "Accepted",
    "397943006": "Planned",
    "441889009": "Denied",
    "74964007": "Other",
}

files_schema = {
    "files": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "pattern": "^[a-zA-Z0-9._-]+\\.(fasta|fa|fastq|fq)(\\.gz)?$",
                },
                "file_sha256sum": {
                    "type": "string",
                },
            },
            "required": ["file_name"],
            "additionalProperties": False,
        },
        "minItems": 1,
        "uniqueItems": True,
    }
}

labs_prefix = ["sequencing_lab", "prime_diagnostic_lab"]
old_labs_schema = {}
for lab in labs_prefix:
    old_labs_schema.update(
        {
            lab + ".date_of_creation": {"$ref": "#/$defs/date-datetime"},
            lab + ".date_of_modification": {"$ref": "#/$defs/date-datetime"},
            lab + ".demis_lab_id": {"type": "string", "pattern": "^(DEMIS-)?[0-9]{5}$"},
            lab + ".federal_state": {"enum": list(federal_states.keys()) + list(federal_states.values())},
            lab + ".city": {"$ref": "#/$defs/sstr"},
            lab + ".name": {"$ref": "#/$defs/sstr"},
            lab + ".postal_code": {"type": "string", "pattern": "^[0-9]{5}$"},
            lab + ".address": {"$ref": "#/$defs/sstr"},
        }
    )


def load_schema(sftp_spec: bool = False) -> Dict[str, Any]:  # noqa: FBT001, FBT002
    p = Path(__file__).parent / "formatChecker/res/schema/SequenceSchema3.2.0.json"
    with Path.open(p) as j:
        schema: Dict[str, Any] = json.load(j)

    # Allow additional properties everywhere
    set_value_from_dict(schema, {"additionalProperties": True})
    # Remove igs_id requirement
    schema["required"].remove("igs_id")
    # remove isolation_source enum currently CVDP specific - not implemented for other pathogens in the dwh
    schema["properties"]["isolation_source"]["$ref"] = "#/$defs/sstr"
    del schema["properties"]["isolation_source"]["enum"]
    # remove requirement for prime_diagnostic_lab -> demis_lab_id
    del schema["properties"]["prime_diagnostic_lab"]["required"]

    # Change schema to be in the sftp specification
    # - Add files specification, exclusive for sftp
    # - Change labs to inline instead of nested
    #    - with optional "DEMIS-" for demis_lab_id and code and display accepted for federal_state
    # - Change upload properties to old names
    # - change pathogen to meldetatbestand
    # - remove enum from isolation_source (specific to CVDP)
    # - Add code in addition to Display name to some properties

    if sftp_spec:
        # Add files to schema, specific to sftp
        schema["properties"].update(files_schema)
        schema["required"].append("files")

        # Convert to inline labs
        del schema["properties"]["prime_diagnostic_lab"]
        del schema["properties"]["sequencing_lab"]
        schema["required"].remove("sequencing_lab")
        schema["properties"].update(old_labs_schema)
        schema["required"].append("sequencing_lab.demis_lab_id")

        # Upload old specification properties
        uploads_specs = {"upload_submitter": "submitter", "repository_link": "upload_url", "repository_id": "public_id"}
        for old, new in uploads_specs.items():
            schema["properties"]["uploads"]["items"]["properties"][old] = schema["properties"]["uploads"]["items"][
                "properties"
            ][new]
            del schema["properties"]["uploads"]["items"]["properties"][new]
        schema["properties"]["uploads"]["items"]["required"].remove("public_id")
        schema["properties"]["uploads"]["items"]["required"].append("repository_id")

        # meldetatbestand
        schema["properties"]["meldetatbestand"] = schema["properties"]["pathogen"]
        del schema["properties"]["pathogen"]
        schema["required"].remove("pathogen")
        schema["required"].append("meldetatbestand")

        # Add code to sequencing reason
        schema["properties"]["sequencing_reason"]["enum"].extend(sequencing_reason.keys())
        # Add code to upload status
        schema["properties"]["uploads"]["items"]["properties"]["upload_status"]["enum"].extend(upload_status.keys())

    return schema
