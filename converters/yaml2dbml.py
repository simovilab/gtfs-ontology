"""Convert GTFS YAML specification to DBML using Jinja2 templates."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml
from jinja2 import Environment, FileSystemLoader


def map_type(field_type: str) -> str:
    """Map GTFS/YAML field types to DBML types.

    Falls back to string for unknown types to keep generation robust.
    """
    if not field_type:
        return "string"

    t = field_type.strip().lower()

    mapping = {
        # textual
        "text": "string",
        "string": "string",
        "url": "string",
        "email": "string",
        "phone number": "string",
        "language code": "string",
        "currency code": "string",
        "timezone": "string",
        "color": "string",
        "id": "string",
        "unique id": "string",
        "foreign id": "string",
        "enum": "string",
        # numeric
        "integer": "int",
        "float": "float",
        "non-negative integer": "int",
        "non-negative float": "float",
        "non-zero integer": "int",
        "non-zero float": "float",
        "positive integer": "int",
        "positive float": "float",
        "latitude": "float",
        "longitude": "float",
        "currency amount": "float",
        # temporal
        "date": "date",
        "time": "time",
        "local time": "time",
        "datetime": "datetime",
        "timestamp": "datetime",
    }

    for key, dbml in mapping.items():
        if t == key or t.startswith(key):
            return dbml

    return "string"


def escape_note(value: str) -> str:
    return value.replace('"', '\\"')


def normalize_table_name(file_name: str) -> str:
    """Turn a GTFS file name into a DB table name.

    Examples:
      - "agency.txt" -> "agency"
      - "locations.geojson" -> "locations"
    """
    base = file_name
    for ext in (".txt", ".geojson"):
        if base.endswith(ext):
            base = base[: -len(ext)]
            break
    return base


def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_tables(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Transform YAML data to a template-friendly structure for DBML generation."""
    fd = (data or {}).get("field_definitions", {})
    files = fd.get("files")

    if not files:
        return []

    # Support both list and mapping forms
    if isinstance(files, dict):
        iterable = (
            {"name": k, **(v or {})}
            for k, v in files.items()  # type: ignore[operator]
        )
    else:
        iterable = files

    tables: List[Dict[str, Any]] = []
    for file_entry in iterable:
        file_name = file_entry.get("name") or file_entry.get("file") or "unknown"
        table_name = normalize_table_name(str(file_name))
        fields = file_entry.get("fields", [])

        pk_assigned = False
        columns: List[Dict[str, Any]] = []
        for field in fields:
            fname = field.get("name", "field")
            ftype = map_type(str(field.get("type", "text")))
            presence = (field.get("presence") or "").strip().lower()
            description = field.get("description") or ""
            notes = field.get("notes")

            attrs: List[str] = []

            # Required -> not null. We avoid enforcing for conditionals to stay conservative.
            if presence.startswith("required"):
                attrs.append("not null")

            # Primary key: explicit flag beats heuristic; else use *_id convention if none set yet.
            is_pk = bool(field.get("primary_key")) or (
                not pk_assigned and str(fname).endswith("_id")
            )
            if is_pk:
                attrs.append("pk")
                pk_assigned = True

            # Default values (quote strings)
            if "default" in field:
                default_val = field["default"]
                if isinstance(default_val, str):
                    attrs.append(f"default: '{default_val}'")
                else:
                    attrs.append(f"default: {default_val}")

            # Compose note from description + notes
            note_parts = []
            if description:
                note_parts.append(str(description))
            if notes:
                note_parts.append(str(notes))
            if note_parts:
                attrs.append(f'note: "{escape_note(" ".join(note_parts))}"')

            columns.append(
                {
                    "name": fname,
                    "type": ftype,
                    "attrs": attrs,
                }
            )

        tables.append({"name": table_name, "columns": columns})

    return tables


def generate_schedule_dbml(overwrite: bool = True) -> Path:
    """Generate schedule DBML from YAML data and Jinja2 template.

    Returns the path to the generated file.
    """
    base_dir = Path(__file__).parent.parent
    yaml_path = base_dir / "serializers" / "schedule.yaml"
    template_dir = base_dir / "converters" / "templates"
    output_dir = base_dir / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "schedule.dbml"
    if not overwrite:
        output_path = output_dir / "schedule.generated.dbml"

    data = load_yaml(yaml_path)
    metadata = data.get("metadata", {})
    tables = build_tables(data)

    env = Environment(
        loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
    )
    template = env.get_template("schedule.dbml.jinja")

    rendered = template.render(metadata=metadata, tables=tables)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"Generated {output_path}")
    return output_path


if __name__ == "__main__":
    # Allow optional flag to avoid overwriting the canonical schema
    no_overwrite = "--no-overwrite" in sys.argv
    generate_schedule_dbml(overwrite=not no_overwrite)
