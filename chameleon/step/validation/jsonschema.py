import functools
import importlib.resources
import logging
import os.path
import pathlib
import typing
from collections import abc
from importlib.resources import abc as importlib_abc

import jsonschema
import referencing
import yaml
from jsonschema.protocols import Validator
from referencing.jsonschema import SchemaRegistry

from chameleon.step.validation import registry

# Default validator used in the app
type DefaultJsonMappingType = jsonschema.Draft202012Validator
DefaultJsonMapping = jsonschema.Draft202012Validator
# Schema registry is id to schema registry
default_schema_registry: SchemaRegistry = SchemaRegistry()
# Schema validators registered for type_id and action_id
validators: abc.MutableMapping[tuple[str, str | None], Validator] = {}

logger = logging.getLogger(__name__)
JSON_EXTENSIONS = (".json", ".yml", ".yaml")


def register_jsonschema_validation(
    *,
    ref: str,
    type_id: str,
    action_id: str | None = None,
    schema_registry: SchemaRegistry | None = None,
):
    key = (type_id, action_id)

    schema_registry_work: SchemaRegistry = guess_schema_registry(schema_registry)

    create_validator(
        ref=ref,
        type_id=type_id,
        action_id=action_id,
        schema_registry=schema_registry_work,
    )

    registry.register(
        type_id=type_id,
        action_id=action_id,
        processor=functools.partial(json_validation_processor, key=key),
    )


def create_validator(
    *,
    ref: str,
    type_id: str,
    action_id: str | None = None,
    schema_registry: SchemaRegistry | None = None,
):
    """Create JSON Schema Validator for given reference and cache it."""

    schema_registry_work = guess_schema_registry(schema_registry)
    key = (type_id, action_id)
    if key not in validators:
        # noinspection PyTypeChecker
        validators[key] = DefaultJsonMapping(
            schema={"$ref": ref},
            format_checker=DefaultJsonMapping.FORMAT_CHECKER,
            registry=schema_registry_work,
        )


def json_validation_processor(value: typing.Any, *, key: tuple[str, str | None]):
    """Basic JSON Schema validation processor."""
    return list(validators[key].iter_errors(value)) or None


def load_schemas(
    paths_or_modules: abc.Sequence[str | pathlib.Path] | str | pathlib.Path,
    aliases: abc.Mapping[str, str] | None = None,
    schema_registry: SchemaRegistry | None = None,
):
    """Load schemas from given paths and apply aliases to them.

    Args:
        paths_or_modules: Paths to read schema files from.
        aliases: Schema id aliases to use.
        schema_registry: Base registry to use to evolve.
    """
    global default_schema_registry  # pylint: disable=global-statement

    schema_registry_work = guess_schema_registry(schema_registry)

    known_schema_ids = set(schema_registry_work)  # it's iterable

    schema_registry_work = schema_registry_work.with_resources(
        obtain_schema_data(paths_or_modules, aliases or {}, known_schema_ids)
    ).crawl()

    update_validators(schema_registry=schema_registry_work)

    # Automagically update default schema registry
    if schema_registry is None:
        default_schema_registry = schema_registry_work

    return schema_registry_work


def update_validators(*, schema_registry: SchemaRegistry | None = None):
    """Update validators using new registry.

    Args:
        schema_registry: Registry to use for new validators.
    """

    schema_registry_work = guess_schema_registry(schema_registry)
    for key, validator in list(validators.items()):
        validators[key] = validator.evolve(registry=schema_registry_work)


def guess_schema_registry(schema_registry: SchemaRegistry | None) -> SchemaRegistry:
    if schema_registry is None:
        schema_registry_work = default_schema_registry
    else:
        schema_registry_work = schema_registry
    return schema_registry_work


def obtain_schema_data(
    paths_or_modules: abc.Sequence[str | pathlib.Path] | str | pathlib.Path,
    aliases: abc.Mapping[str, str],
    known_schema_ids: abc.MutableSet[str],
) -> abc.Iterator[tuple[str, referencing.Resource]]:
    """Read and filter out schema files and return.

    Args:
        paths_or_modules: Paths to read schema files from.
        aliases: Schema id aliases to use.
        known_schema_ids: Already known schema ids.
    """

    for base, filename, schema_data in read_schema_data(paths_or_modules):
        yield from process_schema(
            base, filename, schema_data, aliases, known_schema_ids
        )


def read_schema_data(
    paths_or_modules: abc.Sequence[str | pathlib.Path] | str | pathlib.Path,
) -> abc.Iterator[tuple[str | pathlib.Path, str, typing.Any]]:
    paths: abc.MutableSequence[str | pathlib.Path] = []
    modules: abc.MutableSequence[str] = []

    if isinstance(paths_or_modules, (str, pathlib.Path)):
        paths_or_modules = [paths_or_modules]

    for item in paths_or_modules:
        if isinstance(item, str) and item.startswith("module:"):
            module = item[len("module:") :].strip()
            modules.append(module)
        else:
            paths.append(item)

    yield from read_files(paths)
    yield from read_modules(modules)


def process_schema(
    base: str | pathlib.Path | None,
    filename: str | None,
    schema_data: typing.Any,
    aliases: abc.Mapping[str, str],
    known_schema_ids: abc.MutableSet[str],
) -> abc.Iterator[tuple[str, referencing.Resource]]:
    """Check schema data and return mapping id to a resource.

    Args:
        base: Base for filename to determine schema id.
        filename: Schema filename.
        schema_data: Schema data.
        aliases: schema id aliases.
        known_schema_ids: already known schema ids
    """
    if not check_schema(filename, schema_data):
        return

    schema_resource = referencing.Resource.from_contents(schema_data)
    for schema_id in filter(
        None, obtain_schema_ids(schema_data, base, filename, aliases)
    ):
        if schema_id in known_schema_ids:
            raise ValueError(f"Schema with id {schema_id!r} is already defined")
        known_schema_ids.add(schema_id)
        yield schema_id, schema_resource


def check_schema(filename: str | None, raw_data: typing.Any) -> bool:
    """Check if schema is valid.

    Check is using more strict schema definition to filter out random junk and OpenAPI.
    Schema must be a mapping and contain `$schema` as one of keys.

    If filename is not given, schema must contain `$id` key to be able to identify it.

    OpenAPI support could be added in a future. Currently only JSON Schema is supported.
    Args:
        filename: Filename to log information about in case of an error.
        raw_data: Schema raw data read from file.
    """
    if not isinstance(raw_data, abc.Mapping) or not isinstance(
        raw_data.get("$schema"), str
    ):
        return False

    if (
        filename is None
        and "$id" not in raw_data
        or not isinstance(raw_data["$id"], str)
    ):
        logger.warning(
            "Given schema doesn't contain $id key. "
            "It's impossible to identify such schemas. Skipping"
        )
        return False

    schema_id: str | None = raw_data.get("$id")
    try:
        DefaultJsonMapping.check_schema(raw_data)
        return True
    except jsonschema.SchemaError as e:
        if filename:
            logger.warning(
                "Schema from file %s: not a valid schema. Skipping",
                repr(filename),
                exc_info=e,
            )
        if schema_id:
            logger.warning(
                "Schema with id %s: not a valid schema. Skipping",
                repr(schema_id),
                exc_info=e,
            )
        return False


def obtain_schema_ids(
    schema_data: abc.Mapping[str, typing.Any],
    base: str | pathlib.Path | None,
    filename: str | None,
    aliases: abc.Mapping[str, str],
) -> abc.Iterator[str | None]:
    """Obtain possible schema ids

    Args:
        schema_data: schema data to retrieve information from.
        base: File base, which should be cut out from file name
        filename: Filename, which is an id by itself
        aliases: User defined aliases. Could be aliases to filename or ids
    """
    if filename and base:
        rel: str = os.path.relpath(filename, base)
        yield rel
        yield aliases.get(rel)

    schema_id: typing.Any = schema_data.get("$id")
    if schema_id:
        schema_id_str: str = str(schema_id)
        yield schema_id_str
        yield aliases.get(schema_id_str)


def read_files(
    paths: abc.Sequence[str | pathlib.Path],
) -> abc.Iterator[tuple[str | pathlib.Path, str, typing.Any]]:
    """Read json and yaml files from given paths.

    Args:
        paths: Paths to read json and yaml files from
    """
    for base, filename in list_files_on_filesystem(paths):
        with open(filename, "rb") as f:
            schema_data = yaml.safe_load(f.read())
        yield base, filename, schema_data


def read_modules(
    modules: abc.Sequence[str],
) -> abc.Iterator[tuple[str, str, typing.Any]]:
    """Read json and yaml files from given modules.

    Args:
        modules: Paths to read json and yaml files from
    """
    for base, filename, traversable in files_in_modules(modules):
        schema_data = yaml.safe_load(traversable.read_bytes())
        yield base, filename, schema_data


def is_json_or_yaml(filename: str):
    """Check if filename extension is json or yaml.

    Args:
        filename: filename to check
    """
    return filename.endswith(JSON_EXTENSIONS)


def files_in_modules(
    modules: abc.Sequence[str] | str,
) -> abc.Iterator[tuple[str, str, importlib_abc.Traversable]]:
    for module in modules:
        traversable: importlib_abc.Traversable = importlib.resources.files(module)
        if traversable.is_file() and is_json_or_yaml(traversable.name):
            yield module, traversable.name, traversable
            continue

        for root, _dirs, files in traverse_walk(traversable, root=module):
            yield from (
                (module, f"{root}/{file.name}", file)
                for file in files
                if is_json_or_yaml(file.name)
            )


def list_files_on_filesystem(
    paths: abc.Sequence[str | pathlib.Path] | str | pathlib.Path,
) -> abc.Iterator[tuple[str, str]]:
    """Lists all files from paths.

    If element is a file, return it.
    If argument is directory, traverse it recursively.

    Args:
        paths: list of paths.
    """
    paths_iter: abc.Sequence[str | pathlib.Path]
    if isinstance(paths, (str, pathlib.Path)):
        paths_iter = [paths]
    else:
        paths_iter = paths

    for path in paths_iter:
        if not os.path.exists(path):
            raise ValueError(f"Path {path!r} doesn't exists")

        path_str = str(path)

        if os.path.isfile(path) and is_json_or_yaml(str(path)):
            yield os.path.dirname(path), path_str
            continue

        for root, _dirs, files in os.walk(path):
            yield from (
                (path_str, f"{root}/{filename}")
                for filename in files
                if is_json_or_yaml(filename)
            )


def traverse_walk(
    traversable: importlib_abc.Traversable,
    root: str | None = None,
) -> abc.Iterator[
    tuple[str, list[importlib_abc.Traversable], list[importlib_abc.Traversable]]
]:
    folders = []
    files = []
    for t in traversable.iterdir():
        if t.is_dir():
            folders.append(t)
        else:
            files.append(t)

    yield root or "", folders, files

    for folder in folders:
        yield from traverse_walk(folder, root=f"{root}/{folder}")
