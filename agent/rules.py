import re
import yaml

def load_rules():
    with open("rules/naming.yml") as f:
        return yaml.safe_load(f)

def is_snake_case(name):
    return bool(re.fullmatch(r"[a-z][a-z0-9_]*", name))

def validate_column(col, rules):
    errors = []

    if rules["snake_case"] and not is_snake_case(col.name):
        errors.append("Column must be snake_case")

    if col.cast_type == "boolean":
        if not any(col.name.startswith(p) for p in rules["boolean"]["prefixes"]):
            errors.append("Boolean column must start with is_/has_/can_")

    if col.cast_type == "date":
        if not col.name.endswith(rules["date"]["suffix"]):
            errors.append("Date column must end with _date")

    if col.cast_type == "timestamp":
        if not col.name.endswith(rules["timestamp"]["suffix"]):
            errors.append("Timestamp column must end with _timestamp")

    return errors

def suggest_column_name(col):
    name = col.name

    # camelCase / PascalCase → snake_case
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = name.lower()

    if col.cast_type == "boolean":
        if not name.startswith(("is_", "has_", "can_")):
            name = f"is_{name}"

    if col.cast_type == "date" and not name.endswith("_date"):
        name = f"{name}_date"

    if col.cast_type == "timestamp" and not name.endswith("_timestamp"):
        name = f"{name}_timestamp"

    return name
