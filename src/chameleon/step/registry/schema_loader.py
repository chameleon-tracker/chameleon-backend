import os.path
import pathlib
import typing

import jsonschema
import referencing
import yaml

from chameleon.step.registry import validator_registry


def load_schemas(
    paths: typing.Sequence[str | pathlib.Path], aliases: typing.Mapping[str, str]
):
    validator_registry.schema_registry = (
        validator_registry.schema_registry.with_resources(
            obtain_schema_data(paths, aliases)
        )
    )
    validator_registry.update_validators()


def obtain_schema_data(
    paths: typing.Sequence[str | pathlib.Path], aliases: typing.Mapping[str, str]
):
    schema_ids: typing.Set[str] = set()

    for base, filename in list_files(paths):
        with open(filename, "rb") as f:
            schema_data = yaml.safe_load(f.read())
        if not check_schema(schema_data):
            continue

        schema_resource = referencing.Resource.from_contents(schema_data)
        for schema_id in filter(
            None, obtain_schema_ids(schema_data, base, filename, aliases)
        ):
            if schema_id in schema_ids:
                raise ValueError(f"Schema with id {schema_id!r} is already defined")
            schema_ids.add(schema_id)
            yield schema_id, schema_resource


def check_schema(raw_data: typing.Any):
    if not isinstance(raw_data, typing.Mapping) or "$schema" not in raw_data:
        return False
    try:
        validator_registry.JsonValidator.check_schema(
            raw_data, format_checker=validator_registry.JsonValidator.FORMAT_CHECKER
        )
        return True
    except jsonschema.SchemaError:
        # logger.warn(f"{filename}: not a valid schema", exc_info=e)
        return False


def obtain_schema_ids(
    schema_data: typing.Mapping[str, typing.Any],
    base: str | None,
    filename: str | None,
    aliases: typing.Mapping[str, str],
):
    if filename and base:
        rel = os.path.relpath(filename, base)
        yield rel
        yield aliases.get(rel)

    schema_id = schema_data.get("$id")
    yield schema_id
    yield aliases.get(schema_id)


def is_json_or_yaml(filename: str):
    """Check if filename extension is json or yaml."""

    for ext in (".json", ".yml", ".yaml"):
        if filename.endswith(ext):
            return True
    return False


def filename_tuple(
    base: str, filename: str, directory: str | None = None
) -> tuple[str, str]:
    full_name: str
    if directory:
        full_name = f"{directory}/{filename}"
    else:
        full_name = filename

    return base, full_name


def list_files(paths: typing.Sequence[str]):
    """Lists all files from paths.

    If element is a file, return it.
    If argument is directory, traverse it recursively.

    Args:
        paths: list of paths.
    """
    for path in paths:
        if not os.path.exists(path):
            raise ValueError(f"Path {path!r} doesn't exists")

        if os.path.isfile(path) and is_json_or_yaml(path):
            yield filename_tuple(os.path.basename(path), path)
            continue

        for root, _dirs, files in os.walk(path):
            yield from map(
                lambda filename, directory=root, folder=path: filename_tuple(
                    base=folder, filename=filename, directory=directory
                ),
                filter(is_json_or_yaml, files),
            )
