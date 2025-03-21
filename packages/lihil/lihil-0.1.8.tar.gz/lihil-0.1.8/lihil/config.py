import argparse
import tomllib
from pathlib import Path
from types import GenericAlias, UnionType
from typing import Any, Sequence, Union, cast, get_args, get_origin

from msgspec import convert, field
from msgspec.structs import FieldInfo, fields
from starlette.requests import Request

from lihil.errors import AppConfiguringError
from lihil.interface import MISSING, Record, is_provided
from lihil.plugins.bus import EventBus

StrDict = dict[str, Any]


def get_thread_cnt() -> int:
    import os

    default_max = os.cpu_count() or 1
    return default_max


def format_nested_dict(flat_dict: StrDict) -> StrDict:
    """
    Convert a flat dictionary with dot notation keys to a nested dictionary.

    Example:
        {"oas.title": "API Docs"} -> {"oas": {"title": "API Docs"}}
    """
    result: StrDict = {}

    for key, value in flat_dict.items():
        if "." in key:
            parts = key.split(".")
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            result[key] = value
    return result


def deep_update(original: StrDict, update_data: StrDict) -> StrDict:
    """
    Recursively update a nested dictionary without overwriting entire nested structures.
    """
    for key, value in update_data.items():
        if (
            key in original
            and isinstance(original[key], dict)
            and isinstance(value, dict)
        ):
            deep_update(original[key], cast(Any, value))
        else:
            original[key] = value
    return original


class StoreTrueIfProvided(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ):
        setattr(namespace, self.dest, True)
        # Set a flag to indicate this argument was provided
        setattr(namespace, f"{self.dest}_provided", True)

    def __init__[**P](self, *args: P.args, **kwargs: P.kwargs):
        # Set nargs to 0 for store_true action
        kwargs["nargs"] = 0
        kwargs["default"] = MISSING
        super().__init__(*args, **kwargs)  # type: ignore


def is_lhl_dep(type_: type | GenericAlias):
    "Dependencies that should be injected and managed by lihil"
    return type_ in (Request, EventBus)


class ConfigBase(Record, forbid_unknown_fields=True): ...


class OASConfig(ConfigBase):
    oas_path: str = "/openapi"
    doc_path: str = "/docs"
    problem_path: str = "/problems"
    title: str = "lihil-OpenAPI"
    version: str = "3.1.0"


class ServerConfig(ConfigBase):
    host: str | None = None
    port: int | None = None
    workers: int | None = None
    reload: bool | None = None
    root_path: str | None = None


def parse_field_type(field: FieldInfo):
    "Todo: parse Maybe[int] = MISSING"

    ftype = field.type
    origin = get_origin(ftype)

    if origin is UnionType or origin is Union:
        for targ in get_args(ftype):
            if targ is None:
                continue
            return targ

    return field.type


class AppConfig(ConfigBase):
    is_prod: bool = False
    version: str = "0.1.0"
    max_thread_workers: int = field(default_factory=get_thread_cnt)
    oas: OASConfig = OASConfig()
    server: ServerConfig = ServerConfig()

    @classmethod
    def from_toml(cls, file_path: Path) -> StrDict:
        with open(file_path, "rb") as fp:
            toml = tomllib.load(fp)

        try:
            lihil_config: StrDict = toml["tool"]["lihil"]
        except KeyError:
            try:
                lihil_config: StrDict = toml["lihil"]
            except KeyError:
                raise AppConfiguringError(f"can't find table lihil from {file_path}")
        return lihil_config


def build_parser(config_type: type[AppConfig]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="lihil application configuration")
    cls_fields = fields(config_type)

    for field_info in cls_fields:
        field_name = field_info.name
        field_type = field_info.type

        if isinstance(field_info.default, ConfigBase):
            nested_cls = field_type
            nested_fields = fields(nested_cls)
            for nested_field in nested_fields:
                nested_name = f"{field_name}.{nested_field.name}"
                arg_name = f"--{nested_name}"

                if field_type == bool:
                    parser.add_argument(
                        arg_name,
                        action=StoreTrueIfProvided,
                        default=MISSING,
                        help=f"Set {field_name} (default: {field_info.default})",
                    )
                else:
                    parser.add_argument(
                        arg_name,
                        type=parse_field_type(nested_field),
                        default=MISSING,
                        help=f"Set {nested_name} (default: {nested_field.default})",
                    )

        else:
            arg_name = f"--{field_name}"
            if field_type == bool:
                parser.add_argument(
                    arg_name,
                    action=StoreTrueIfProvided,
                    default=MISSING,
                    help=f"Set {field_name} (default: {field_info.default})",
                )
            elif field_info.required:
                default_value = field_info.default_factory()
                parser.add_argument(
                    arg_name,
                    type=field_type,
                    default=MISSING,
                    help=f"Set {field_name} (default: {default_value})",
                )
            else:
                parser.add_argument(
                    arg_name,
                    type=field_type,
                    default=MISSING,
                    help=f"Set {field_name} (default: {field_info.default})",
                )
    return parser


def config_from_cli(config_type: type[AppConfig]) -> StrDict | None:
    parser = build_parser(config_type)
    known_args = parser.parse_known_args()[0]
    args = known_args.__dict__

    # Filter out _provided flags and keep only provided values
    cli_args: StrDict = {
        k: v for k, v in args.items() if is_provided(v) and not k.endswith("_provided")
    }

    if not cli_args:
        return None

    config_dict = format_nested_dict(cli_args)
    return config_dict


def config_from_file(
    config_file: Path | str | None, *, config_type: type[AppConfig] = AppConfig
) -> AppConfig:
    if config_file is None:
        return config_type()  # everything default

    if isinstance(config_file, str):
        file_path = Path(config_file)
    else:
        file_path = config_file

    if not file_path.exists():
        raise AppConfiguringError(f"path {file_path} not exist")

    file_ext = file_path.suffix[1:]

    if file_ext == "toml":
        config_dict = config_type.from_toml(file_path)
    else:
        raise AppConfiguringError(f"Not supported file type {file_ext}")

    cli_config = config_from_cli(config_type)
    if cli_config:
        deep_update(config_dict, cli_config)

    config = convert(config_dict, config_type)
    return config
